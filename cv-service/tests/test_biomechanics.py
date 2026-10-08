"""Unit tests for Biomechanical Angle Calculations and Kinematics."""
import numpy as np
import pytest
from app.core.biomechanics import (
    compute_angle_3points,
    compute_vector_angle_to_vertical,
    compute_kinematics,
    compute_movement_deviation
)


def test_compute_angle_90_degrees():
    # Right-angled triangle: A=(0, 1), B=(0, 0), C=(1, 0) -> vertex B is 90 deg
    a = [0.0, 1.0]
    b = [0.0, 0.0]
    c = [1.0, 0.0]
    angle = compute_angle_3points(a, b, c)
    assert pytest.approx(angle, abs=1e-3) == 90.0


def test_compute_angle_180_straight_line():
    # Straight line: A=(-1, 0), B=(0, 0), C=(1, 0) -> 180 deg
    a = [-1.0, 0.0]
    b = [0.0, 0.0]
    c = [1.0, 0.0]
    angle = compute_angle_3points(a, b, c)
    assert pytest.approx(angle, abs=1e-3) == 180.0


def test_compute_angle_45_degrees():
    a = [1.0, 1.0]
    b = [0.0, 0.0]
    c = [1.0, 0.0]
    angle = compute_angle_3points(a, b, c)
    assert pytest.approx(angle, abs=1e-3) == 45.0


def test_compute_angle_3d_coordinates():
    # 3D points
    a = [0.0, 1.0, 0.0]
    b = [0.0, 0.0, 0.0]
    c = [0.0, 0.0, 1.0]
    angle = compute_angle_3points(a, b, c)
    assert pytest.approx(angle, abs=1e-3) == 90.0


def test_compute_angle_zero_length_fallback():
    # Degenerate case where points coincide
    a = [0.0, 0.0]
    b = [0.0, 0.0]
    c = [1.0, 0.0]
    angle = compute_angle_3points(a, b, c)
    assert angle == 0.0


def test_compute_vector_angle_to_vertical():
    # Torso standing perfectly straight upright: bottom=(0, 1), top=(0, 0)
    # in image space (y goes down), top has smaller y than bottom
    p_bottom = [100.0, 200.0]
    p_top = [100.0, 100.0]
    angle = compute_vector_angle_to_vertical(p_bottom, p_top)
    assert pytest.approx(angle, abs=1e-2) == 0.0

    # Tilted 45 degrees forward
    p_top_tilted = [200.0, 100.0]
    angle_tilted = compute_vector_angle_to_vertical(p_bottom, p_top_tilted)
    assert pytest.approx(angle_tilted, abs=1e-2) == 45.0


def test_compute_kinematics():
    # Test constant velocity motion
    # p_t moves 10 units each second at 10 fps (dt = 0.1)
    fps = 10.0
    dt = 0.1
    positions = np.array([[0.0], [1.0], [2.0], [3.0]], dtype=np.float32)
    vel, acc = compute_kinematics(positions, fps=fps)

    # Velocity for step 1, 2, 3 should be delta_p / dt = 1.0 / 0.1 = 10.0
    assert pytest.approx(vel[1, 0], abs=1e-3) == 10.0
    assert pytest.approx(vel[2, 0], abs=1e-3) == 10.0
    assert pytest.approx(vel[3, 0], abs=1e-3) == 10.0

    # Acceleration of constant velocity is 0
    assert pytest.approx(acc[2, 0], abs=1e-3) == 0.0
    assert pytest.approx(acc[3, 0], abs=1e-3) == 0.0


def test_compute_movement_deviation():
    observed = [90.0, 95.0, 85.0]
    reference = 90.0
    # |0| + |5| + |-5| = 10 / 3 = 3.3333...
    dev = compute_movement_deviation(observed, reference)
    assert pytest.approx(dev, abs=1e-3) == (10.0 / 3.0)
