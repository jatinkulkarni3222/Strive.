"""Unit tests for Body Scale Normalization (Equation 1.9.3)."""
import numpy as np
import pytest
from app.core.normalizer import BodyScaleNormalizer


def test_body_scale_normalization_scale_invariance():
    normalizer = BodyScaleNormalizer()

    # Create dummy landmarks (33, 2)
    landmarks_1 = np.zeros((33, 2), dtype=np.float32)
    # Left shoulder: 11, Right shoulder: 12 (mid-shoulder at (0, 10))
    landmarks_1[11] = [-2.0, 10.0]
    landmarks_1[12] = [2.0, 10.0]
    # Left hip: 23, Right hip: 24 (mid-hip at (0, 0)) -> torso length = 10.0
    landmarks_1[23] = [-1.5, 0.0]
    landmarks_1[24] = [1.5, 0.0]
    # Knee at (0, -8)
    landmarks_1[25] = [-1.5, -8.0]

    norm_1, center_1, s_1 = normalizer.normalize_frame(landmarks_1)
    assert pytest.approx(s_1, abs=1e-3) == 10.0
    # Center mid-hip is (0, 0)
    assert pytest.approx(center_1[0], abs=1e-3) == 0.0
    assert pytest.approx(center_1[1], abs=1e-3) == 0.0

    # Scale by 2.5x and translate by (+50, +100) (e.g. closer camera, shifted in frame)
    scale_factor = 2.5
    offset = np.array([50.0, 100.0], dtype=np.float32)
    landmarks_2 = landmarks_1 * scale_factor + offset

    norm_2, center_2, s_2 = normalizer.normalize_frame(landmarks_2)
    assert pytest.approx(s_2, abs=1e-3) == 10.0 * scale_factor

    # Normalized knee coordinates should be identical across both scales!
    np.testing.assert_allclose(norm_1[25], norm_2[25], atol=1e-4)
