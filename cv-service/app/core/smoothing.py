"""Temporal Smoothing Module.

Implements Equation (1.9.4):
    p^_t = alpha * p_t + (1 - alpha) * p^_{t-1}
as well as Savitzky-Golay polynomial filtering to suppress high-frequency jitter
from camera sensor noise and keypoint jitter while preserving athletic turning points.
"""
import numpy as np
from scipy.signal import savgol_filter
from typing import Optional


class TemporalSmoother:
    """Applies temporal smoothing across keypoint coordinate sequences."""

    def __init__(self, alpha: float = 0.65, savgol_window: int = 7, savgol_polyorder: int = 2):
        """
        Parameters
        ----------
        alpha : float
            Smoothing weight for Exponential Moving Average (Equation 1.9.4), 0 < alpha <= 1.
        savgol_window : int
            Window length for Savitzky-Golay filter (must be positive odd integer).
        savgol_polyorder : int
            Polynomial order for Savitzky-Golay filter (must be < savgol_window).
        """
        self.alpha = float(alpha)
        # Savgol window must be odd
        self.savgol_window = savgol_window if savgol_window % 2 == 1 else savgol_window + 1
        self.savgol_polyorder = savgol_polyorder

    def smooth_ema(self, sequence: np.ndarray) -> np.ndarray:
        """Apply Exponential Moving Average across the temporal axis (Equation 1.9.4).

        Parameters
        ----------
        sequence : np.ndarray
            Shape (T, ...) where axis 0 is time.
        """
        if sequence.shape[0] <= 1:
            return sequence.copy()

        smoothed = np.zeros_like(sequence, dtype=np.float32)
        smoothed[0] = sequence[0]

        for t in range(1, sequence.shape[0]):
            smoothed[t] = self.alpha * sequence[t] + (1.0 - self.alpha) * smoothed[t - 1]

        return smoothed

    def smooth_savgol(self, sequence: np.ndarray) -> np.ndarray:
        """Apply Savitzky-Golay filter across the time dimension.

        Falls back gracefully to EMA if time steps are smaller than window size.
        """
        T = sequence.shape[0]
        if T <= self.savgol_polyorder + 1:
            return self.smooth_ema(sequence)

        # Ensure window length is odd and does not exceed sequence length
        win = min(self.savgol_window, T if T % 2 == 1 else T - 1)
        if win <= self.savgol_polyorder:
            return self.smooth_ema(sequence)

        # Apply along time axis (axis=0)
        try:
            return savgol_filter(sequence, window_length=win, polyorder=self.savgol_polyorder, axis=0)
        except Exception:
            return self.smooth_ema(sequence)

    def smooth(self, sequence: np.ndarray, method: str = "savgol") -> np.ndarray:
        """Main smoothing interface."""
        if method == "savgol":
            return self.smooth_savgol(sequence)
        return self.smooth_ema(sequence)
