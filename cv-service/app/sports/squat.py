"""Squat Biomechanical Assessment Strategy.

Evaluates squat repetitions, range of motion (ROM), trunk posture,
knee valgus, spinal deviations, and calculates weighted performance scores.
"""
import numpy as np
from typing import Dict, Any, List, Optional
from app.sports.base import BaseSportAssessment
from app.core.biomechanics import (
    compute_angle_3points,
    compute_vector_angle_to_vertical,
    compute_movement_deviation
)
from app.config import MEDICAL_DISCLAIMER


class SquatAssessment(BaseSportAssessment):
    """End-to-end squat repetition counter, form checker, and injury risk analyzer."""

    # Keypoint indices
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    def __init__(self, config: Dict[str, Any], fps: float = 30.0):
        super().__init__("squat", config, fps)
        self.ref_form = config.get("reference_form", {})
        self.rep_thresh = config.get("rep_thresholds", {})
        self.weights = config.get("scoring_weights", {})

        # Repetition State Machine: 'standing', 'descending', 'bottom', 'ascending'
        self.state = "standing"
        self.rep_count = 0
        self.reps_data: List[Dict[str, Any]] = []

        # Current rep tracking buffers
        self.current_rep_start_frame = 0
        self.current_rep_min_knee_angle = 180.0
        self.current_rep_bottom_frame = 0
        self.current_rep_torso_leans: List[float] = []
        self.current_rep_valgus_flags: List[bool] = []

        # Frame history for annotation & global metrics
        self.frame_states: Dict[int, Dict[str, Any]] = {}
        self.all_knee_angles: List[float] = []
        self.all_hip_angles: List[float] = []
        self.all_torso_leans: List[float] = []
        self.active_warning: Optional[str] = None

        # Cumulative rule triggers
        self.injury_insights: List[Dict[str, Any]] = []
        self.valgus_detected_count = 0
        self.forward_lean_count = 0
        self.rounded_back_count = 0

    def process_frame(
        self,
        frame_idx: int,
        timestamp: float,
        landmarks_norm: np.ndarray,
        visibilities: np.ndarray,
        frame_confidence: float
    ) -> Dict[str, Any]:
        """Process frame landmarks for squat assessment."""
        self.frame_count += 1

        # Determine dominant/visible side
        left_knee_vis = visibilities[self.LEFT_KNEE]
        right_knee_vis = visibilities[self.RIGHT_KNEE]

        # Knee angles
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

        if left_knee_vis > 0.5 and right_knee_vis > 0.5:
            knee_angle = (left_knee + right_knee) / 2.0
            bilateral = True
        elif left_knee_vis >= right_knee_vis:
            knee_angle = left_knee
            bilateral = False
        else:
            knee_angle = right_knee
            bilateral = False

        # Midpoints for torso & hips
        mid_shoulder = (landmarks_norm[self.LEFT_SHOULDER] + landmarks_norm[self.RIGHT_SHOULDER]) / 2.0
        mid_hip = (landmarks_norm[self.LEFT_HIP] + landmarks_norm[self.RIGHT_HIP]) / 2.0
        mid_knee = (landmarks_norm[self.LEFT_KNEE] + landmarks_norm[self.RIGHT_KNEE]) / 2.0

        # Hip angle
        hip_angle = compute_angle_3points(mid_shoulder, mid_hip, mid_knee)

        # Torso lean relative to vertical (up is -y)
        torso_lean = compute_vector_angle_to_vertical(mid_hip[:2], mid_shoulder[:2])

        # Knee Valgus check (frontal/bilateral view: knee distance vs ankle distance)
        knee_valgus_flag = False
        if bilateral and visibilities[self.LEFT_ANKLE] > 0.4 and visibilities[self.RIGHT_ANKLE] > 0.4:
            knee_dist = np.linalg.norm(landmarks_norm[self.LEFT_KNEE, :2] - landmarks_norm[self.RIGHT_KNEE, :2])
            ankle_dist = np.linalg.norm(landmarks_norm[self.LEFT_ANKLE, :2] - landmarks_norm[self.RIGHT_ANKLE, :2])
            if ankle_dist > 0.05:
                valgus_ratio = knee_dist / ankle_dist
                min_ratio = self.ref_form.get("knee_valgus_ratio_min", 0.85)
                # Check for valgus collapse during squat depth
                if knee_angle < 120.0 and valgus_ratio < min_ratio:
                    knee_valgus_flag = True

        self.all_knee_angles.append(knee_angle)
        self.all_hip_angles.append(hip_angle)
        self.all_torso_leans.append(torso_lean)

        # Repetition State Machine
        std_knee = self.rep_thresh.get("standing_knee_angle", 160.0)
        desc_knee = self.rep_thresh.get("descent_knee_angle", 130.0)
        bot_knee = self.rep_thresh.get("bottom_knee_angle", 100.0)
        min_duration = self.rep_thresh.get("min_rep_duration_sec", 0.8)

        active_warning = None

        if self.state == "standing":
            if knee_angle < desc_knee:
                self.state = "descending"
                self.current_rep_start_frame = frame_idx
                self.current_rep_min_knee_angle = knee_angle
                self.current_rep_torso_leans = [torso_lean]
                self.current_rep_valgus_flags = [knee_valgus_flag]

        elif self.state == "descending":
            self.current_rep_torso_leans.append(torso_lean)
            self.current_rep_valgus_flags.append(knee_valgus_flag)
            if knee_angle < self.current_rep_min_knee_angle:
                self.current_rep_min_knee_angle = knee_angle
                self.current_rep_bottom_frame = frame_idx

            if knee_angle <= bot_knee:
                self.state = "bottom"
            elif knee_angle > desc_knee + 15.0:
                # Aborted or incomplete twitch returning up
                self.state = "standing"

        elif self.state == "bottom":
            self.current_rep_torso_leans.append(torso_lean)
            self.current_rep_valgus_flags.append(knee_valgus_flag)
            if knee_angle < self.current_rep_min_knee_angle:
                self.current_rep_min_knee_angle = knee_angle
                self.current_rep_bottom_frame = frame_idx

            # Transition out of bottom into ascent
            if knee_angle > self.current_rep_min_knee_angle + 12.0:
                self.state = "ascending"

        elif self.state == "ascending":
            self.current_rep_torso_leans.append(torso_lean)
            self.current_rep_valgus_flags.append(knee_valgus_flag)
            if knee_angle >= std_knee:
                # Rep completed!
                rep_duration = (frame_idx - self.current_rep_start_frame) / max(self.fps, 1.0)
                if rep_duration >= min_duration:
                    self.rep_count += 1
                    rep_info = {
                        "rep_number": self.rep_count,
                        "duration_sec": round(rep_duration, 2),
                        "min_knee_angle": round(self.current_rep_min_knee_angle, 1),
                        "max_torso_lean": round(max(self.current_rep_torso_leans, default=0.0), 1),
                        "valgus_detected": any(self.current_rep_valgus_flags),
                        "start_frame": self.current_rep_start_frame,
                        "bottom_frame": self.current_rep_bottom_frame,
                        "end_frame": frame_idx
                    }
                    self.reps_data.append(rep_info)

                    if rep_info["valgus_detected"]:
                        self.valgus_detected_count += 1
                    if rep_info["max_torso_lean"] > self.ref_form.get("torso_lean_max_deg", 35.0):
                        self.forward_lean_count += 1

                self.state = "standing"

        # Form warnings for live HUD
        if knee_valgus_flag:
            active_warning = "Knee Valgus (knees caving inward)"
        elif torso_lean > self.ref_form.get("torso_lean_max_deg", 35.0) + 5.0 and self.state in ["descending", "bottom"]:
            active_warning = "Excessive Forward Lean"

        self.active_warning = active_warning

        frame_state = {
            "knee_angle": round(knee_angle, 1),
            "hip_angle": round(hip_angle, 1),
            "torso_lean": round(torso_lean, 1),
            "phase": self.state,
            "rep_count": self.rep_count,
            "active_warning": active_warning,
            "confidence": frame_confidence
        }
        self.frame_states[frame_idx] = frame_state
        return frame_state

    def get_hud_state(self, frame_idx: int) -> Dict[str, Any]:
        """Retrieve HUD parameters for rendering this frame."""
        return self.frame_states.get(frame_idx, {
            "knee_angle": 180.0,
            "hip_angle": 180.0,
            "torso_lean": 0.0,
            "phase": "standing",
            "rep_count": self.rep_count,
            "active_warning": None,
            "confidence": 1.0
        })

    def finalize_assessment(self) -> Dict[str, Any]:
        """Generate final performance scores, feature vector, and injury insights."""
        # 1. Range of Motion (ROM) Score [0 - 100]
        # Target: bottom knee angle between 70° and 100°
        if self.reps_data:
            mean_bottom_knee = float(np.mean([r["min_knee_angle"] for r in self.reps_data]))
        elif self.all_knee_angles:
            # Fallback if reps were partial or continuous
            mean_bottom_knee = float(np.min(self.all_knee_angles))
        else:
            mean_bottom_knee = 180.0

        if mean_bottom_knee <= 95.0:
            rom_score = 100.0
        elif mean_bottom_knee <= 120.0:
            # Linear decay from 100 down to 60
            rom_score = 100.0 - ((mean_bottom_knee - 95.0) / 25.0) * 40.0
        else:
            rom_score = max(20.0, 60.0 - ((mean_bottom_knee - 120.0) / 30.0) * 40.0)

        # 2. Form Deviation (Equation 1.9.7: D = (1/N) * sum(|x_i - x^_i|))
        ref_bottom_knee = (self.ref_form.get("knee_angle_bottom_min", 70.0) + self.ref_form.get("knee_angle_bottom_max", 100.0)) / 2.0
        knee_deviation = compute_movement_deviation(
            [r["min_knee_angle"] for r in self.reps_data] if self.reps_data else [mean_bottom_knee],
            ref_bottom_knee
        )

        ref_torso_lean = 25.0  # reference good neutral incline
        torso_deviation = compute_movement_deviation(
            [r["max_torso_lean"] for r in self.reps_data] if self.reps_data else [float(np.mean(self.all_torso_leans or [0.0]))],
            ref_torso_lean
        )

        overall_deviation = round(float((knee_deviation + torso_deviation) / 2.0), 2)
        form_score = max(30.0, 100.0 - (overall_deviation * 1.5))

        # 3. Repetition Consistency Score [0 - 100]
        if len(self.reps_data) >= 2:
            durations = [r["duration_sec"] for r in self.reps_data]
            depths = [r["min_knee_angle"] for r in self.reps_data]
            cv_duration = float(np.std(durations) / max(np.mean(durations), 1e-4))
            cv_depth = float(np.std(depths) / max(np.mean(depths), 1e-4))
            consistency_score = max(30.0, 100.0 - ((cv_duration + cv_depth) / 2.0 * 100.0))
        elif len(self.reps_data) == 1:
            consistency_score = 85.0
        else:
            consistency_score = 40.0

        # 4. Kinematic Stability [0 - 100]
        kinematic_stability = 90.0 if overall_deviation < 15.0 else max(50.0, 90.0 - overall_deviation)

        # 5. Performance Score (Equation 1.9.6: S = sum(w_i * f_i) where sum(w_i) = 1)
        w_rom = self.weights.get("depth_rom", 0.35)
        w_form = self.weights.get("form_deviation", 0.35)
        w_cons = self.weights.get("rep_consistency", 0.20)
        w_kin = self.weights.get("kinematic_stability", 0.10)

        final_score = (
            w_rom * rom_score +
            w_form * form_score +
            w_cons * consistency_score +
            w_kin * kinematic_stability
        )
        final_score = round(float(np.clip(final_score, 0.0, 100.0)), 1)

        # 6. Injury-Risk Rules & Recommendations
        injury_insights = []
        overall_risk_level = "LOW"

        if self.valgus_detected_count > 0:
            overall_risk_level = "HIGH" if self.valgus_detected_count > 1 else "MEDIUM"
            injury_insights.append({
                "rule": "KNEE_VALGUS",
                "severity": "HIGH",
                "message": f"Knee valgus (knees caving inward) was observed during {self.valgus_detected_count} repetition(s).",
                "biomechanical_implication": "Significantly elevates dynamic valgus moment on the ACL and patellofemoral joint.",
                "corrective_cues": "Focus on driving knees outward over second toe; incorporate banded glute bridge and monster walks."
            })

        if self.forward_lean_count > 0:
            if overall_risk_level == "LOW":
                overall_risk_level = "MEDIUM"
            injury_insights.append({
                "rule": "EXCESSIVE_FORWARD_LEAN",
                "severity": "MEDIUM",
                "message": f"Excessive trunk forward lean (> 35 deg) detected on {self.forward_lean_count} repetition(s).",
                "biomechanical_implication": "Increases spinal lumbar shear forces and decreases quad activation.",
                "corrective_cues": "Maintain chest elevation, engage thoracic extensors, and test ankle dorsiflexion mobility."
            })

        if self.reps_data and mean_bottom_knee > 105.0:
            injury_insights.append({
                "rule": "INSUFFICIENT_DEPTH",
                "severity": "LOW",
                "message": f"Average depth ({mean_bottom_knee:.1f} deg) did not reach parallel depth.",
                "biomechanical_implication": "Decreased recruitment of posterior chain and suboptimal athletic development.",
                "corrective_cues": "Perform box squats or goblet squats to reinforce depth awareness."
            })

        if not injury_insights:
            injury_insights.append({
                "rule": "OPTIMAL_FORM",
                "severity": "NONE",
                "message": "Excellent squat biomechanics! Bilateral symmetry and trunk stability maintained throughout.",
                "biomechanical_implication": "Balanced load distribution across kinetic chain.",
                "corrective_cues": "Maintain current training progression."
            })

        # 7. Feature Vector (Equation 1.9.5: F = [theta_1, ..., theta_n, v, a, ROM, consistency])
        feature_vector = [
            round(mean_bottom_knee, 2),
            round(float(np.mean(self.all_hip_angles or [180.0])), 2),
            round(float(np.mean(self.all_torso_leans or [0.0])), 2),
            round(float(np.max(self.all_torso_leans or [0.0])), 2),
            round(rom_score, 2),
            round(form_score, 2),
            round(consistency_score, 2),
            round(overall_deviation, 2),
            float(self.rep_count)
        ]

        return {
            "sport": "squat",
            "rep_count": self.rep_count,
            "performance_score": final_score,
            "sub_scores": {
                "range_of_motion": round(rom_score, 1),
                "form_technique": round(form_score, 1),
                "consistency": round(consistency_score, 1),
                "kinematic_stability": round(kinematic_stability, 1)
            },
            "movement_deviation": overall_deviation,
            "average_bottom_knee_angle": round(mean_bottom_knee, 1),
            "reps_detail": self.reps_data,
            "injury_risk_level": overall_risk_level,
            "injury_insights": injury_insights,
            "feature_vector": feature_vector,
            "disclaimer": MEDICAL_DISCLAIMER
        }
