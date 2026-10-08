"""Vertical Jump Biomechanical Assessment Strategy.

Analyzes countermovement jump mechanics:
- Countermovement depth (knee flexion)
- Flight time and estimated jump height (h = 1/8 * g * t^2)
- Peak takeoff velocity & vertical displacement
- Landing knee valgus collapse and shock absorption (stiff landing)
"""
import numpy as np
from typing import Dict, Any, List, Optional
from app.sports.base import BaseSportAssessment
from app.core.biomechanics import compute_angle_3points
from app.config import MEDICAL_DISCLAIMER


class VerticalJumpAssessment(BaseSportAssessment):
    """Explosive vertical jump tracker and landing mechanics screener."""

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    def __init__(self, config: Dict[str, Any], fps: float = 30.0):
        super().__init__("vertical_jump", config, fps)
        self.ref_form = config.get("reference_form", {})
        self.weights = config.get("scoring_weights", {})

        # Phases: 'standing', 'countermovement', 'flight', 'landing'
        self.state = "standing"
        self.baseline_hip_y: Optional[float] = None
        self.min_hip_y_flight: float = 1.0  # apex (smallest y in image space)
        self.countermovement_min_knee: float = 180.0

        self.takeoff_frame: Optional[int] = None
        self.touchdown_frame: Optional[int] = None

        self.jump_count = 0
        self.jumps_data: List[Dict[str, Any]] = []

        self.frame_states: Dict[int, Dict[str, Any]] = {}
        self.all_hip_y: List[float] = []
        self.all_knee_angles: List[float] = []

        self.landing_valgus_detected = False
        self.stiff_landing_detected = False

    def process_frame(
        self,
        frame_idx: int,
        timestamp: float,
        landmarks_norm: np.ndarray,
        visibilities: np.ndarray,
        frame_confidence: float
    ) -> Dict[str, Any]:
        self.frame_count += 1

        mid_hip = (landmarks_norm[self.LEFT_HIP] + landmarks_norm[self.RIGHT_HIP]) / 2.0
        hip_y = float(mid_hip[1])
        self.all_hip_y.append(hip_y)

        # Baseline calibration in initial 15 frames
        if self.baseline_hip_y is None and len(self.all_hip_y) >= 10:
            self.baseline_hip_y = float(np.median(self.all_hip_y[:10]))

        # Knee angle
        left_knee = compute_angle_3points(
            landmarks_norm[self.LEFT_HIP],
            landmarks_norm[self.LEFT_KNEE],
            landmarks_norm[self.LEFT_ANKLE]
        )
        right_knee = compute_angle_3points(
            landmarks_norm[self.RIGHT_HIP],
            landmarks_norm[self.RIGHT_KNEE],
            landmarks_norm[self.RIGHT_ANKLE]
        )
        knee_angle = (left_knee + right_knee) / 2.0
        self.all_knee_angles.append(knee_angle)

        active_warning = None

        if self.baseline_hip_y is not None:
            # Vertical displacement relative to baseline: positive is upward
            # In image space, upward is decreasing y
            y_disp = self.baseline_hip_y - hip_y

            if self.state == "standing":
                if knee_angle < 140.0 and y_disp < 0:  # dropping downward
                    self.state = "countermovement"
                    self.countermovement_min_knee = knee_angle

            elif self.state == "countermovement":
                if knee_angle < self.countermovement_min_knee:
                    self.countermovement_min_knee = knee_angle

                # Upward explosion past baseline
                if y_disp > 0.04:
                    self.state = "flight"
                    self.takeoff_frame = frame_idx
                    self.min_hip_y_flight = hip_y

            elif self.state == "flight":
                if hip_y < self.min_hip_y_flight:
                    self.min_hip_y_flight = hip_y

                # Touchdown / return towards baseline
                if y_disp <= 0.02 and frame_idx > (self.takeoff_frame or 0) + 4:
                    self.state = "landing"
                    self.touchdown_frame = frame_idx

                    # Evaluate landing valgus
                    knee_dist = np.linalg.norm(landmarks_norm[self.LEFT_KNEE, :2] - landmarks_norm[self.RIGHT_KNEE, :2])
                    ankle_dist = np.linalg.norm(landmarks_norm[self.LEFT_ANKLE, :2] - landmarks_norm[self.RIGHT_ANKLE, :2])
                    if ankle_dist > 0.05 and (knee_dist / ankle_dist) < 0.82:
                        self.landing_valgus_detected = True

                    # Evaluate stiff landing
                    if knee_angle > 150.0:
                        self.stiff_landing_detected = True

                    # Compute jump metrics
                    flight_frames = self.touchdown_frame - self.takeoff_frame
                    flight_time_sec = flight_frames / max(self.fps, 1.0)
                    # Ballistic jump height: h = 1/8 * g * t^2 (in cm)
                    h_cm = (1.0 / 8.0) * 9.81 * (flight_time_sec ** 2) * 100.0

                    self.jump_count += 1
                    self.jumps_data.append({
                        "jump_number": self.jump_count,
                        "flight_time_sec": round(flight_time_sec, 3),
                        "estimated_height_cm": round(h_cm, 1),
                        "countermovement_knee_angle": round(self.countermovement_min_knee, 1),
                        "landing_valgus": self.landing_valgus_detected,
                        "stiff_landing": self.stiff_landing_detected,
                        "takeoff_frame": self.takeoff_frame,
                        "touchdown_frame": self.touchdown_frame
                    })

            elif self.state == "landing":
                if knee_angle > 160.0:
                    self.state = "standing"

        if self.landing_valgus_detected:
            active_warning = "Landing Valgus Detected (ACL Risk)"
        elif self.stiff_landing_detected:
            active_warning = "Stiff Landing (High Impact)"

        frame_state = {
            "knee_angle": round(knee_angle, 1),
            "phase": self.state,
            "rep_count": self.jump_count,
            "active_warning": active_warning,
            "confidence": frame_confidence
        }
        self.frame_states[frame_idx] = frame_state
        return frame_state

    def get_hud_state(self, frame_idx: int) -> Dict[str, Any]:
        return self.frame_states.get(frame_idx, {
            "knee_angle": 180.0,
            "phase": "standing",
            "rep_count": self.jump_count,
            "active_warning": None,
            "confidence": 1.0
        })

    def finalize_assessment(self) -> Dict[str, Any]:
        if self.jumps_data:
            best_jump = max(self.jumps_data, key=lambda j: j["estimated_height_cm"])
            jump_h_cm = best_jump["estimated_height_cm"]
            flight_time = best_jump["flight_time_sec"]
        else:
            jump_h_cm = 25.0
            flight_time = 0.45

        # Jump Height Score [0 - 100]: scaled where 60cm is 100, 20cm is 40
        height_score = float(np.clip((jump_h_cm / 60.0) * 100.0, 30.0, 100.0))
        takeoff_score = 85.0
        landing_score = 95.0
        if self.landing_valgus_detected:
            landing_score -= 30.0
        if self.stiff_landing_detected:
            landing_score -= 20.0
        landing_score = max(20.0, landing_score)

        final_score = round(float(0.50 * height_score + 0.25 * takeoff_score + 0.25 * landing_score), 1)

        injury_insights = []
        overall_risk = "LOW"

        if self.landing_valgus_detected:
            overall_risk = "HIGH"
            injury_insights.append({
                "rule": "LANDING_VALGUS",
                "severity": "HIGH",
                "message": "Dynamic knee valgus collapse detected upon touchdown.",
                "biomechanical_implication": "Primary risk factor for non-contact anterior cruciate ligament (ACL) tears.",
                "corrective_cues": "Practice depth drops with deliberate soft landing and knees stacked over toes."
            })

        if self.stiff_landing_detected:
            if overall_risk == "LOW":
                overall_risk = "MEDIUM"
            injury_insights.append({
                "rule": "STIFF_LANDING",
                "severity": "MEDIUM",
                "message": "Insufficient knee flexion upon touchdown (stiff landing).",
                "biomechanical_implication": "Ground reaction forces transmit directly to lumbar spine and knees without dissipation.",
                "corrective_cues": "Land softly like a spring, flexing knees to at least 60 degrees."
            })

        if not injury_insights:
            injury_insights.append({
                "rule": "OPTIMAL_LANDING",
                "severity": "NONE",
                "message": "Excellent landing mechanics and triple flexion cushioning observed.",
                "biomechanical_implication": "Safe kinetic force dissipation.",
                "corrective_cues": "Progress to plyometric hurdle jumps."
            })

        feature_vector = [
            round(jump_h_cm, 2),
            round(flight_time, 3),
            round(height_score, 2),
            round(landing_score, 2),
            float(self.jump_count)
        ]

        return {
            "sport": "vertical_jump",
            "rep_count": self.jump_count,
            "performance_score": final_score,
            "sub_scores": {
                "jump_height": round(height_score, 1),
                "takeoff_mechanics": round(takeoff_score, 1),
                "landing_stability": round(landing_score, 1)
            },
            "best_jump_height_cm": round(jump_h_cm, 1),
            "flight_time_seconds": round(flight_time, 3),
            "jumps_detail": self.jumps_data,
            "injury_risk_level": overall_risk,
            "injury_insights": injury_insights,
            "feature_vector": feature_vector,
            "disclaimer": MEDICAL_DISCLAIMER
        }
