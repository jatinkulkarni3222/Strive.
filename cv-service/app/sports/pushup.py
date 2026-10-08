"""Push-up Biomechanical Assessment Strategy.

Evaluates push-up repetitions, range of motion (ROM), elbow flare,
body alignment (plank neutrality/hip sagging), and calculates performance scores.
"""
import numpy as np
from typing import Dict, Any, List, Optional
from app.sports.base import BaseSportAssessment
from app.core.biomechanics import (
    compute_angle_3points,
    compute_movement_deviation
)
from app.config import MEDICAL_DISCLAIMER


class PushupAssessment(BaseSportAssessment):
    """End-to-end push-up repetition counter, form checker, and injury risk analyzer."""

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    def __init__(self, config: Dict[str, Any], fps: float = 30.0):
        super().__init__("pushup", config, fps)
        self.ref_form = config.get("reference_form", {})
        self.rep_thresh = config.get("rep_thresholds", {})
        self.weights = config.get("scoring_weights", {})

        # Repetition State Machine: 'top', 'descending', 'bottom', 'ascending'
        self.state = "top"
        self.rep_count = 0
        self.reps_data: List[Dict[str, Any]] = []

        self.current_rep_start_frame = 0
        self.current_rep_min_elbow_angle = 180.0
        self.current_rep_bottom_frame = 0
        self.current_rep_body_alignments: List[float] = []
        self.current_rep_flare_flags: List[bool] = []

        self.frame_states: Dict[int, Dict[str, Any]] = {}
        self.all_elbow_angles: List[float] = []
        self.all_body_alignments: List[float] = []
        self.active_warning: Optional[str] = None

        self.flare_detected_count = 0
        self.hip_sagging_count = 0

    def process_frame(
        self,
        frame_idx: int,
        timestamp: float,
        landmarks_norm: np.ndarray,
        visibilities: np.ndarray,
        frame_confidence: float
    ) -> Dict[str, Any]:
        self.frame_count += 1

        # Visible arm determination
        left_elbow_vis = visibilities[self.LEFT_ELBOW]
        right_elbow_vis = visibilities[self.RIGHT_ELBOW]

        left_elbow = compute_angle_3points(
            landmarks_norm[self.LEFT_SHOULDER],
            landmarks_norm[self.LEFT_ELBOW],
            landmarks_norm[self.LEFT_WRIST]
        )
        right_elbow = compute_angle_3points(
            landmarks_norm[self.RIGHT_SHOULDER],
            landmarks_norm[self.RIGHT_ELBOW],
            landmarks_norm[self.RIGHT_WRIST]
        )

        if left_elbow_vis > 0.5 and right_elbow_vis > 0.5:
            elbow_angle = (left_elbow + right_elbow) / 2.0
        elif left_elbow_vis >= right_elbow_vis:
            elbow_angle = left_elbow
        else:
            elbow_angle = right_elbow

        # Body alignment (Plank neutrality: shoulder - hip - ankle)
        mid_shoulder = (landmarks_norm[self.LEFT_SHOULDER] + landmarks_norm[self.RIGHT_SHOULDER]) / 2.0
        mid_hip = (landmarks_norm[self.LEFT_HIP] + landmarks_norm[self.RIGHT_HIP]) / 2.0
        mid_ankle = (landmarks_norm[self.LEFT_ANKLE] + landmarks_norm[self.RIGHT_ANKLE]) / 2.0

        body_alignment = compute_angle_3points(mid_shoulder, mid_hip, mid_ankle)

        # Elbow flare check: angle between torso vector (hip->shoulder) and arm vector (shoulder->elbow)
        arm_vec = landmarks_norm[self.LEFT_ELBOW, :2] - landmarks_norm[self.LEFT_SHOULDER, :2]
        torso_vec = mid_hip[:2] - mid_shoulder[:2]
        norm_arm = np.linalg.norm(arm_vec)
        norm_torso = np.linalg.norm(torso_vec)
        if norm_arm > 1e-5 and norm_torso > 1e-5:
            flare_cosine = np.dot(arm_vec, torso_vec) / (norm_arm * norm_torso)
            flare_angle = float(np.degrees(np.arccos(np.clip(flare_cosine, -1.0, 1.0))))
        else:
            flare_angle = 45.0

        flare_flag = flare_angle > self.ref_form.get("elbow_flare_max_deg", 75.0) and elbow_angle < 120.0
        sagging_flag = body_alignment < self.ref_form.get("trunk_alignment_min", 160.0)

        self.all_elbow_angles.append(elbow_angle)
        self.all_body_alignments.append(body_alignment)

        top_angle = self.rep_thresh.get("top_elbow_angle", 155.0)
        bot_angle = self.rep_thresh.get("bottom_elbow_angle", 95.0)
        min_duration = self.rep_thresh.get("min_rep_duration_sec", 0.7)

        active_warning = None

        # State Machine
        if self.state == "top":
            if elbow_angle < 135.0:
                self.state = "descending"
                self.current_rep_start_frame = frame_idx
                self.current_rep_min_elbow_angle = elbow_angle
                self.current_rep_body_alignments = [body_alignment]
                self.current_rep_flare_flags = [flare_flag]

        elif self.state == "descending":
            self.current_rep_body_alignments.append(body_alignment)
            self.current_rep_flare_flags.append(flare_flag)
            if elbow_angle < self.current_rep_min_elbow_angle:
                self.current_rep_min_elbow_angle = elbow_angle
                self.current_rep_bottom_frame = frame_idx

            if elbow_angle <= bot_angle:
                self.state = "bottom"
            elif elbow_angle > 145.0:
                self.state = "top"

        elif self.state == "bottom":
            self.current_rep_body_alignments.append(body_alignment)
            self.current_rep_flare_flags.append(flare_flag)
            if elbow_angle < self.current_rep_min_elbow_angle:
                self.current_rep_min_elbow_angle = elbow_angle
                self.current_rep_bottom_frame = frame_idx

            if elbow_angle > self.current_rep_min_elbow_angle + 12.0:
                self.state = "ascending"

        elif self.state == "ascending":
            self.current_rep_body_alignments.append(body_alignment)
            self.current_rep_flare_flags.append(flare_flag)
            if elbow_angle >= top_angle:
                rep_duration = (frame_idx - self.current_rep_start_frame) / max(self.fps, 1.0)
                if rep_duration >= min_duration:
                    self.rep_count += 1
                    rep_info = {
                        "rep_number": self.rep_count,
                        "duration_sec": round(rep_duration, 2),
                        "min_elbow_angle": round(self.current_rep_min_elbow_angle, 1),
                        "mean_body_alignment": round(float(np.mean(self.current_rep_body_alignments or [180.0])), 1),
                        "flare_detected": any(self.current_rep_flare_flags),
                        "start_frame": self.current_rep_start_frame,
                        "bottom_frame": self.current_rep_bottom_frame,
                        "end_frame": frame_idx
                    }
                    self.reps_data.append(rep_info)

                    if rep_info["flare_detected"]:
                        self.flare_detected_count += 1
                    if rep_info["mean_body_alignment"] < 160.0:
                        self.hip_sagging_count += 1

                self.state = "top"

        if flare_flag:
            active_warning = "Elbow Flare (> 75 deg)"
        elif sagging_flag:
            active_warning = "Sagging Hips / Arching Back"

        self.active_warning = active_warning

        frame_state = {
            "elbow_angle": round(elbow_angle, 1),
            "body_alignment": round(body_alignment, 1),
            "phase": self.state,
            "rep_count": self.rep_count,
            "active_warning": active_warning,
            "confidence": frame_confidence
        }
        self.frame_states[frame_idx] = frame_state
        return frame_state

    def get_hud_state(self, frame_idx: int) -> Dict[str, Any]:
        return self.frame_states.get(frame_idx, {
            "elbow_angle": 180.0,
            "body_alignment": 180.0,
            "phase": "top",
            "rep_count": self.rep_count,
            "active_warning": None,
            "confidence": 1.0
        })

    def finalize_assessment(self) -> Dict[str, Any]:
        # 1. ROM score
        if self.reps_data:
            mean_bottom_elbow = float(np.mean([r["min_elbow_angle"] for r in self.reps_data]))
        elif self.all_elbow_angles:
            mean_bottom_elbow = float(np.min(self.all_elbow_angles))
        else:
            mean_bottom_elbow = 180.0

        if mean_bottom_elbow <= 90.0:
            rom_score = 100.0
        elif mean_bottom_elbow <= 110.0:
            rom_score = 100.0 - ((mean_bottom_elbow - 90.0) / 20.0) * 40.0
        else:
            rom_score = max(20.0, 60.0 - ((mean_bottom_elbow - 110.0) / 30.0) * 40.0)

        # 2. Form deviation
        ref_bottom_elbow = 85.0
        elbow_dev = compute_movement_deviation(
            [r["min_elbow_angle"] for r in self.reps_data] if self.reps_data else [mean_bottom_elbow],
            ref_bottom_elbow
        )
        ref_alignment = 175.0  # neutral plank
        align_dev = compute_movement_deviation(
            [r["mean_body_alignment"] for r in self.reps_data] if self.reps_data else [float(np.mean(self.all_body_alignments or [175.0]))],
            ref_alignment
        )
        overall_dev = round(float((elbow_dev + align_dev) / 2.0), 2)
        form_score = max(30.0, 100.0 - (overall_dev * 1.5))

        # 3. Consistency
        if len(self.reps_data) >= 2:
            durations = [r["duration_sec"] for r in self.reps_data]
            cv_duration = float(np.std(durations) / max(np.mean(durations), 1e-4))
            consistency_score = max(30.0, 100.0 - (cv_duration * 100.0))
        elif len(self.reps_data) == 1:
            consistency_score = 85.0
        else:
            consistency_score = 40.0

        kinematic_stability = 90.0 if overall_dev < 15.0 else max(50.0, 90.0 - overall_dev)

        w_rom = self.weights.get("rom", 0.35)
        w_form = self.weights.get("form_deviation", 0.35)
        w_cons = self.weights.get("rep_consistency", 0.20)
        w_kin = self.weights.get("kinematic_stability", 0.10)

        final_score = round(float(np.clip(
            w_rom * rom_score + w_form * form_score + w_cons * consistency_score + w_kin * kinematic_stability,
            0.0, 100.0
        )), 1)

        # Injury insights
        injury_insights = []
        overall_risk = "LOW"

        if self.flare_detected_count > 0:
            overall_risk = "HIGH" if self.flare_detected_count > 1 else "MEDIUM"
            injury_insights.append({
                "rule": "ELBOW_FLARE",
                "severity": "HIGH",
                "message": f"Elbow flare (> 75 deg from torso) detected on {self.flare_detected_count} repetition(s).",
                "biomechanical_implication": "Imposes excessive anterior shoulder impingement and rotator cuff strain.",
                "corrective_cues": "Tuck elbows to approximately 45 degrees relative to ribcage (arrowhead shape)."
            })

        if self.hip_sagging_count > 0:
            if overall_risk == "LOW":
                overall_risk = "MEDIUM"
            injury_insights.append({
                "rule": "SAGGING_HIPS",
                "severity": "MEDIUM",
                "message": f"Hip sagging / lumbar hyperextension observed during {self.hip_sagging_count} repetition(s).",
                "biomechanical_implication": "Increases spinal lumbar lordotic compression and reflects core fatigue.",
                "corrective_cues": "Squeeze glutes and engage rectus abdominis to lock in a rigid plank position."
            })

        if not injury_insights:
            injury_insights.append({
                "rule": "OPTIMAL_FORM",
                "severity": "NONE",
                "message": "Excellent push-up technique! Stable neutral spine and optimal elbow tucking.",
                "biomechanical_implication": "Even load distribution across pectorals, triceps, and core.",
                "corrective_cues": "Maintain current pressing volume."
            })

        feature_vector = [
            round(mean_bottom_elbow, 2),
            round(float(np.mean(self.all_body_alignments or [180.0])), 2),
            round(rom_score, 2),
            round(form_score, 2),
            round(consistency_score, 2),
            round(overall_dev, 2),
            float(self.rep_count)
        ]

        return {
            "sport": "pushup",
            "rep_count": self.rep_count,
            "performance_score": final_score,
            "sub_scores": {
                "range_of_motion": round(rom_score, 1),
                "form_technique": round(form_score, 1),
                "consistency": round(consistency_score, 1),
                "kinematic_stability": round(kinematic_stability, 1)
            },
            "movement_deviation": overall_dev,
            "average_bottom_elbow_angle": round(mean_bottom_elbow, 1),
            "reps_detail": self.reps_data,
            "injury_risk_level": overall_risk,
            "injury_insights": injury_insights,
            "feature_vector": feature_vector,
            "disclaimer": MEDICAL_DISCLAIMER
        }
