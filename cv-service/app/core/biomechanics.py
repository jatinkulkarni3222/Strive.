"""Biomechanical Analysis & Kinematics Module.

Implements:
1. Joint Angle Calculation (Equation 1.9.1):
   theta = arccos(( (A - B) . (C - B) ) / ( ||A - B|| * ||C - B|| ))
2. Velocity and Acceleration (Equation 1.9.2):
   v_t = (p_t - p_{t-1}) / delta_t
   a_t = (v_t - v_{t-1}) / delta_t
3. Movement Deviation (Equation 1.9.7):
   D = (1 / N) * sum(|x_i - x^_i|)
"""
import numpy as np
from typing import Tuple, List, Optional, Union


def compute_angle_3points(
    a: Union[np.ndarray, List[float]],
    b: Union[np.ndarray, List[float]],
    c: Union[np.ndarray, List[float]]
) -> float:
    """Calculate joint angle theta in degrees at vertex B formed by points A-B-C.

    Equation (1.9.1):
        theta = arccos( ((A - B) . (C - B)) / (||A - B|| * ||C - B||) )

    Parameters
    ----------
    a : 2D or 3D coordinate of landmark A
    b : 2D or 3D coordinate of landmark B (the joint center)
    c : 2D or 3D coordinate of landmark C

    Returns
    -------
    float
        Angle in degrees [0.0, 180.0]
    """
    va = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    vc = np.asarray(c, dtype=np.float64) - np.asarray(b, dtype=np.float64)

    norm_va = np.linalg.norm(va)
    norm_vc = np.linalg.norm(vc)

    if norm_va < 1e-7 or norm_vc < 1e-7:
        return 0.0

    cosine = np.dot(va, vc) / (norm_va * norm_vc)
    # Clip to avoid floating point precision escaping [-1.0, 1.0]
    cosine = np.clip(cosine, -1.0, 1.0)
    angle_rad = np.arccos(cosine)
    return float(np.degrees(angle_rad))


def compute_vector_angle_to_vertical(
    p_bottom: Union[np.ndarray, List[float]],
    p_top: Union[np.ndarray, List[float]]
) -> float:
    """Calculate angle of a segment (e.g. torso from hip to shoulder) relative to the vertical axis.

    Vertical in image space points upward along -Y: vector (0, -1).

    Returns
    -------
    float
        Angle in degrees [0.0, 180.0] where 0 is purely vertical.
    """
    # 2D coordinates: x, y
    v = np.array([p_top[0] - p_bottom[0], p_top[1] - p_bottom[1]], dtype=np.float64)
    # Image space: y increases downwards, so vertical up is (0, -1)
    v_vertical = np.array([0.0, -1.0], dtype=np.float64)

    norm_v = np.linalg.norm(v)
    if norm_v < 1e-7:
        return 0.0

    cosine = np.dot(v, v_vertical) / norm_v
    cosine = np.clip(cosine, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosine)))


def compute_kinematics(
    positions: np.ndarray,
    fps: float
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute velocity and acceleration across time frames (Equation 1.9.2).

    v_t = (p_t - p_{t-1}) / delta_t
    a_t = (v_t - v_{t-1}) / delta_t

    Parameters
    ----------
    positions : np.ndarray
        Shape (T, D) or (T, K, D)
    fps : float
        Frames per second (> 0).

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        velocities: same shape as positions (first frame padded with 0)
        accelerations: same shape as positions (first 2 frames padded with 0)
    """
    if fps <= 0:
        fps = 30.0
    dt = 1.0 / fps

    T = positions.shape[0]
    velocities = np.zeros_like(positions, dtype=np.float32)
    accelerations = np.zeros_like(positions, dtype=np.float32)

    if T > 1:
        # v_t = (p_t - p_{t-1}) / dt
        velocities[1:] = (positions[1:] - positions[:-1]) / dt

    if T > 2:
        # a_t = (v_t - v_{t-1}) / dt
        accelerations[2:] = (velocities[2:] - velocities[1:-1]) / dt

    return velocities, accelerations


def compute_movement_deviation(
    observed_values: List[float],
    reference_target: float
) -> float:
    """Compute mean absolute deviation from reference good-form target (Equation 1.9.7).

    D = (1 / N) * sum(|x_i - x^_i|)
    """
    if not observed_values:
        return 0.0
    arr = np.asarray(observed_values, dtype=np.float64)
    return float(np.mean(np.abs(arr - reference_target)))
