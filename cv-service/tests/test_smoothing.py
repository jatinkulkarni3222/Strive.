"""Unit tests for Temporal Smoothing filters (Savitzky-Golay and EMA)."""
import numpy as np
import pytest
from app.core.smoothing import TemporalSmoother


def test_ema_smoothing_formula():
    alpha = 0.5
    smoother = TemporalSmoother(alpha=alpha)
    seq = np.array([10.0, 20.0, 30.0], dtype=np.float32)

    smoothed = smoother.smooth_ema(seq)
    # p^_0 = 10.0
    # p^_1 = 0.5 * 20.0 + 0.5 * 10.0 = 15.0
    # p^_2 = 0.5 * 30.0 + 0.5 * 15.0 = 22.5
    assert pytest.approx(smoothed[0], abs=1e-3) == 10.0
    assert pytest.approx(smoothed[1], abs=1e-3) == 15.0
    assert pytest.approx(smoothed[2], abs=1e-3) == 22.5


def test_savgol_smoothing_suppresses_noise():
    smoother = TemporalSmoother(savgol_window=7, savgol_polyorder=2)
    # Sinusoid with high-frequency noise
    t = np.linspace(0, np.pi, 25)
    clean_signal = np.sin(t)
    noisy_signal = clean_signal + 0.1 * np.array([1, -1] * 12 + [1])

    smoothed = smoother.smooth_savgol(noisy_signal)
    # Variance of difference to clean signal should be lower in smoothed
    noisy_error = np.mean((noisy_signal - clean_signal) ** 2)
    smoothed_error = np.mean((smoothed - clean_signal) ** 2)
    assert smoothed_error < noisy_error


def test_smoothing_fallback_on_short_sequence():
    smoother = TemporalSmoother(savgol_window=15, savgol_polyorder=2)
    # Sequence shorter than window
    short_seq = np.array([5.0, 8.0, 12.0], dtype=np.float32)
    result = smoother.smooth(short_seq, method="savgol")
    assert result.shape == short_seq.shape
    assert not np.any(np.isnan(result))
