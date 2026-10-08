"""Body-Scale Normalization Module.

Implements Equation (1.9.3):
    p'_i = (p_i - p_c) / s
where p_i is the detected position of landmark i, p_c is the body reference center
(mid-hip or mid-torso), and s is the body-scale normalization factor (torso length:
distance from mid-shoulder to mid-hip).
"""
import numpy as np
from typing import Tuple, Optional, Dict, Any


class BodyScaleNormalizer:
    """Normalizes 2D and 3D pose coordinates across athletes and camera distances."""

    # MediaPipe landmark indices
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_HIP = 23
    RIGHT_HIP = 24

    def __init__(self, min_torso_scale: float = 1e-4):
        self.min_torso_scale = min_torso_scale

    def compute_reference_frame(
        self, landmarks: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Compute reference center p_c and normalization scale factor s for a single frame.

        Parameters
        ----------
        landmarks : np.ndarray
            Shape (33, 2) or (33, 3) representing detected landmark coordinates.

        Returns
        -------
        Tuple[np.ndarray, float]
            p_c: Reference center point (mid-hip).
            s: Normalization scale factor (distance between mid-shoulder and mid-hip).
        """
        # Mid-shoulder
        left_shoulder = landmarks[self.LEFT_SHOULDER]
        right_shoulder = landmarks[self.RIGHT_SHOULDER]
        mid_shoulder = (left_shoulder + right_shoulder) / 2.0

        # Mid-hip
        left_hip = landmarks[self.LEFT_HIP]
        right_hip = landmarks[self.RIGHT_HIP]
        mid_hip = (left_hip + right_hip) / 2.0

        # Reference center p_c is mid-hip
        p_c = mid_hip

        # Scale factor s is Euclidean distance between mid-shoulder and mid-hip (torso length)
        s = float(np.linalg.norm(mid_shoulder - mid_hip))
        if s < self.min_torso_scale:
            # Fallback scale if torso is occluded or collapsed
            s = 1.0

        return p_c, s

    def normalize_frame(self, landmarks: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """Normalize a single frame of landmarks.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray, float]
            normalized_landmarks: Shape (33, d)
            p_c: Reference center
            scale: Normalization factor s
        """
        p_c, s = self.compute_reference_frame(landmarks)
        normalized = (landmarks - p_c) / s
        return normalized, p_c, s

    def normalize_sequence(self, sequence: np.ndarray) -> np.ndarray:
        """Normalize an entire temporal sequence of landmarks.

        Parameters
        ----------
        sequence : np.ndarray
            Shape (T, 33, 2) or (T, 33, 3)

        Returns
        -------
        np.ndarray
            Normalized sequence of identical shape.
        """
        T = sequence.shape[0]
        normalized_seq = np.zeros_like(sequence, dtype=np.float32)

        # Compute robust median torso scale across all valid frames to prevent frame-to-frame breathing artifact
        scales = []
        for t in range(T):
            _, s = self.compute_reference_frame(sequence[t])
            if s > self.min_torso_scale and s != 1.0:
                scales.append(s)

        median_s = float(np.median(scales)) if scales else 1.0
        if median_s < self.min_torso_scale:
            median_s = 1.0

        for t in range(T):
            left_hip = sequence[t, self.LEFT_HIP]
            right_hip = sequence[t, self.RIGHT_HIP]
            p_c = (left_hip + right_hip) / 2.0
            normalized_seq[t] = (sequence[t] - p_c) / median_s

        return normalized_seq
