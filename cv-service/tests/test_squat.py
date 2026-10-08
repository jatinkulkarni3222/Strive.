"""Unit tests for Squat Assessment Strategy and Biomechanical Rules."""
import numpy as np
import pytest
from app.sports.squat import SquatAssessment
from app.config import SPORT_CONFIGS


def _generate_synthetic_squat_landmarks(
    total_frames: int = 90,
    knee_bottom_angle: float = 85.0,
    torso_lean_deg: float = 20.0,
    valgus_collapse: bool = False
) -> np.ndarray:
    """Generate (total_frames, 33, 3) landmarks simulating a squat cycle."""
    frames = np.zeros((total_frames, 33, 3), dtype=np.float32)

    # Standard body layout in normalized [0, 1] coords
    # Shoulders (11, 12), Hips (23, 24), Knees (25, 26), Ankles (27, 28)
    shoulder_y = 0.25
    hip_y = 0.50
    knee_y_base = 0.70
    ankle_y = 0.90

    # Knee angle curve over time: begins 170°, dips to knee_bottom_angle at frame 45, returns to 170°
    t = np.linspace(0, np.pi, total_frames)
    knee_curve = 170.0 - (170.0 - knee_bottom_angle) * np.sin(t)

    for i in range(total_frames):
        k_angle = knee_curve[i]
        theta_rad = np.radians(k_angle)

        # Base ankle & knee positions
        knee_base_y = 0.65
        ankle_y = 0.90
        L_thigh = 0.22
        L_shin = ankle_y - knee_base_y

        # Knee y dips slightly as athlete squats
        squat_depth_progress = (170.0 - k_angle) / (170.0 - knee_bottom_angle + 1e-4)
        knee_y = knee_base_y + 0.08 * squat_depth_progress

        # Compute hip location from knee using angle k_angle
        # Leg bends backward/downward
        th_rad = np.pi - theta_rad
        hip_x_offset = L_thigh * np.sin(th_rad)
        hip_y = knee_y - L_thigh * np.cos(th_rad)

        # Valgus simulation: knees collapse inwards horizontally
        valgus_inward = 0.045 if (valgus_collapse and k_angle < 110.0) else 0.0

        # Torso lean offset: shoulders relative to hip
        rad_lean = np.radians(torso_lean_deg)
        torso_len = 0.22
        shoulder_x_offset = torso_len * np.sin(rad_lean)
        shoulder_y = hip_y - torso_len * np.cos(rad_lean)

        # Hips (23, 24)
        frames[i, 23] = [0.46 - hip_x_offset, hip_y, 0.0]
        frames[i, 24] = [0.54 - hip_x_offset, hip_y, 0.0]

        # Knees (25, 26): aligned with ankles in normal squat
        frames[i, 25] = [0.44 + valgus_inward, knee_y, 0.0]
        frames[i, 26] = [0.56 - valgus_inward, knee_y, 0.0]

        # Ankles (27, 28)
        frames[i, 27] = [0.44, ankle_y, 0.0]
        frames[i, 28] = [0.56, ankle_y, 0.0]

        # Shoulders (11, 12)
        frames[i, 11] = [0.45 - hip_x_offset + shoulder_x_offset, shoulder_y, 0.0]
        frames[i, 12] = [0.55 - hip_x_offset + shoulder_x_offset, shoulder_y, 0.0]

    return frames


def test_squat_rep_counting_and_high_score():
    config = SPORT_CONFIGS["squat"]
    assessment = SquatAssessment(config=config, fps=30.0)

    # 3 repetitions: 90 frames each = 270 frames total (9 seconds)
    total_frames = 270
    frames_rep1 = _generate_synthetic_squat_landmarks(90, knee_bottom_angle=85.0, torso_lean_deg=22.0)
    frames_rep2 = _generate_synthetic_squat_landmarks(90, knee_bottom_angle=88.0, torso_lean_deg=24.0)
    frames_rep3 = _generate_synthetic_squat_landmarks(90, knee_bottom_angle=86.0, torso_lean_deg=23.0)
    full_sequence = np.concatenate([frames_rep1, frames_rep2, frames_rep3], axis=0)

    visibilities = np.ones((33,), dtype=np.float32)

    for i in range(total_frames):
        assessment.process_frame(
            frame_idx=i,
            timestamp=i / 30.0,
            landmarks_norm=full_sequence[i],
            visibilities=visibilities,
            frame_confidence=0.95
        )

    result = assessment.finalize_assessment()

    # Rep count should be exactly 3
    assert result["rep_count"] == 3
    assert len(result["reps_detail"]) == 3
    # Performance score should be high (> 80) for excellent depth and neutral lean
    assert result["performance_score"] >= 80.0
    assert result["sub_scores"]["range_of_motion"] >= 90.0
    assert result["injury_risk_level"] == "LOW"
    assert "Not a medical diagnosis" in result["disclaimer"]


def test_squat_knee_valgus_rule_detection():
    config = SPORT_CONFIGS["squat"]
    assessment = SquatAssessment(config=config, fps=30.0)

    # 2 reps with knee valgus inward collapse
    rep1 = _generate_synthetic_squat_landmarks(90, knee_bottom_angle=85.0, valgus_collapse=True)
    rep2 = _generate_synthetic_squat_landmarks(90, knee_bottom_angle=85.0, valgus_collapse=True)
    full_sequence = np.concatenate([rep1, rep2], axis=0)

    visibilities = np.ones((33,), dtype=np.float32)

    for i in range(180):
        assessment.process_frame(
            frame_idx=i,
            timestamp=i / 30.0,
            landmarks_norm=full_sequence[i],
            visibilities=visibilities,
            frame_confidence=0.92
        )

    result = assessment.finalize_assessment()
    assert result["rep_count"] == 2
    # Valgus rule should be triggered and reflected in injury insights
    valgus_insights = [ins for ins in result["injury_insights"] if ins["rule"] == "KNEE_VALGUS"]
    assert len(valgus_insights) > 0
    assert result["injury_risk_level"] in ["MEDIUM", "HIGH"]


def test_squat_excessive_forward_lean_rule():
    config = SPORT_CONFIGS["squat"]
    assessment = SquatAssessment(config=config, fps=30.0)

    # 2 reps with severe forward trunk lean (48 degrees)
    rep1 = _generate_synthetic_squat_landmarks(90, knee_bottom_angle=90.0, torso_lean_deg=48.0)
    rep2 = _generate_synthetic_squat_landmarks(90, knee_bottom_angle=90.0, torso_lean_deg=48.0)
    full_sequence = np.concatenate([rep1, rep2], axis=0)

    visibilities = np.ones((33,), dtype=np.float32)

    for i in range(180):
        assessment.process_frame(
            frame_idx=i,
            timestamp=i / 30.0,
            landmarks_norm=full_sequence[i],
            visibilities=visibilities,
            frame_confidence=0.90
        )

    result = assessment.finalize_assessment()
    assert result["rep_count"] == 2
    lean_insights = [ins for ins in result["injury_insights"] if ins["rule"] == "EXCESSIVE_FORWARD_LEAN"]
    assert len(lean_insights) > 0
