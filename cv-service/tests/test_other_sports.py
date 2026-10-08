"""Unit tests for Push-up and Vertical Jump Assessment Strategies."""
import numpy as np
import pytest
from app.sports.pushup import PushupAssessment
from app.sports.vertical_jump import VerticalJumpAssessment
from app.config import SPORT_CONFIGS


def _generate_synthetic_pushup(total_frames=90, elbow_bottom=80.0, flare=False, sag=False):
    """Generate pushup landmarks sequence with accurate elbow flexion."""
    frames = np.zeros((total_frames, 33, 3), dtype=np.float32)
    t = np.linspace(0, np.pi, total_frames)
    elbow_curve = 165.0 - (165.0 - elbow_bottom) * np.sin(t)

    for i in range(total_frames):
        e_angle = elbow_curve[i]
        theta_rad = np.radians(e_angle)

        # Shoulder (11, 12)
        frames[i, 11] = [0.35, 0.35, 0.0]
        frames[i, 12] = [0.45, 0.35, 0.0]

        # Elbow (13, 14): vertex B
        elbow_y = 0.50
        flare_x = 0.08 if (flare and e_angle < 110.0) else 0.0
        frames[i, 13] = [0.35 - flare_x, elbow_y, 0.0]
        frames[i, 14] = [0.45 + flare_x, elbow_y, 0.0]

        # Wrist (15, 16): place using exact angle e_angle
        # BA = shoulder - elbow = (0, -0.15)
        # BC = wrist - elbow
        L_forearm = 0.15
        wrist_x = 0.35 + L_forearm * np.sin(np.pi - theta_rad)
        wrist_y = elbow_y + L_forearm * np.cos(np.pi - theta_rad)
        frames[i, 15] = [wrist_x, wrist_y, 0.0]
        frames[i, 16] = [wrist_x + 0.10, wrist_y, 0.0]

        # Hips (23, 24)
        hip_y = 0.48 if sag else 0.36
        frames[i, 23] = [0.65, hip_y, 0.0]
        frames[i, 24] = [0.75, hip_y, 0.0]

        # Ankles (27, 28)
        frames[i, 27] = [0.88, 0.37, 0.0]
        frames[i, 28] = [0.98, 0.37, 0.0]

    return frames


def test_pushup_rep_and_form():
    config = SPORT_CONFIGS["pushup"]
    assessment = PushupAssessment(config=config, fps=30.0)

    rep1 = _generate_synthetic_pushup(90, elbow_bottom=80.0)
    rep2 = _generate_synthetic_pushup(90, elbow_bottom=85.0)
    seq = np.concatenate([rep1, rep2], axis=0)

    vis = np.ones((33,), dtype=np.float32)
    for i in range(180):
        assessment.process_frame(i, i / 30.0, seq[i], vis, 0.95)

    res = assessment.finalize_assessment()
    assert res["rep_count"] == 2
    assert res["performance_score"] >= 75.0
    assert "Not a medical diagnosis" in res["disclaimer"]


def test_pushup_elbow_flare_rule():
    config = SPORT_CONFIGS["pushup"]
    assessment = PushupAssessment(config=config, fps=30.0)

    rep1 = _generate_synthetic_pushup(90, elbow_bottom=80.0, flare=True)
    rep2 = _generate_synthetic_pushup(90, elbow_bottom=80.0, flare=True)
    seq = np.concatenate([rep1, rep2], axis=0)

    vis = np.ones((33,), dtype=np.float32)
    for i in range(180):
        assessment.process_frame(i, i / 30.0, seq[i], vis, 0.95)

    res = assessment.finalize_assessment()
    assert res["rep_count"] == 2
    flare_ins = [x for x in res["injury_insights"] if x["rule"] == "ELBOW_FLARE"]
    assert len(flare_ins) > 0


def test_vertical_jump_mechanics():
    config = SPORT_CONFIGS["vertical_jump"]
    assessment = VerticalJumpAssessment(config=config, fps=30.0)

    # 120 frames (4 seconds)
    frames = np.zeros((120, 33, 3), dtype=np.float32)
    for i in range(120):
        if i < 20:
            hip_y = 0.50
            k_angle = 175.0
        elif 20 <= i < 40:
            # dip: knee flexes to 100
            dip_p = (i - 20) / 20.0
            hip_y = 0.50 + 0.10 * np.sin(dip_p * np.pi)
            k_angle = 175.0 - 80.0 * np.sin(dip_p * np.pi)
        elif 40 <= i < 70:
            # flight
            fl_p = (i - 40) / 30.0
            hip_y = 0.50 - 0.15 * np.sin(fl_p * np.pi)
            k_angle = 170.0
        else:
            hip_y = 0.50
            k_angle = 170.0

        th_rad = np.radians(k_angle)
        knee_y = hip_y + 0.20
        ankle_y = 0.90

        # Position knee so that angle(hip, knee, ankle) equals k_angle
        # BA = hip - knee = (0, -0.20)
        # BC = ankle - knee
        L_shin = ankle_y - knee_y
        ankle_x_off = L_shin * np.sin(np.pi - th_rad)

        frames[i, 23] = [0.45, hip_y, 0.0]
        frames[i, 24] = [0.55, hip_y, 0.0]
        frames[i, 25] = [0.44, knee_y, 0.0]
        frames[i, 26] = [0.56, knee_y, 0.0]
        frames[i, 27] = [0.44 + ankle_x_off, ankle_y, 0.0]
        frames[i, 28] = [0.56 + ankle_x_off, ankle_y, 0.0]

    vis = np.ones((33,), dtype=np.float32)
    for i in range(120):
        assessment.process_frame(i, i / 30.0, frames[i], vis, 0.95)

    res = assessment.finalize_assessment()
    assert res["sport"] == "vertical_jump"
    assert res["rep_count"] >= 1
    assert res["best_jump_height_cm"] > 0
    assert res["performance_score"] > 50.0
