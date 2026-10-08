"""Base Sports Assessment Interface (Strategy Pattern).

Allows extensible addition of any sport/exercise assessment (Squat, Push-up, Vertical Jump, etc.).
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import numpy as np


class BaseSportAssessment(ABC):
    """Abstract Strategy interface for all sports movement evaluations."""

    def __init__(self, sport_name: str, config: Dict[str, Any], fps: float = 30.0):
        self.sport_name = sport_name
        self.config = config
        self.fps = fps
        self.frame_count = 0

    @abstractmethod
    def process_frame(
        self,
        frame_idx: int,
        timestamp: float,
        landmarks_norm: np.ndarray,
        visibilities: np.ndarray,
        frame_confidence: float
    ) -> Dict[str, Any]:
        """Analyze a single video frame.

        Parameters
        ----------
        frame_idx : int
            Current 0-indexed frame number.
        timestamp : float
            Frame timestamp in seconds.
        landmarks_norm : np.ndarray
            Normalized coordinates shape (33, 3).
        visibilities : np.ndarray
            Confidence scores shape (33,).
        frame_confidence : float
            Average visibility for this frame.

        Returns
        -------
        Dict[str, Any]
            Instantaneous metrics for this frame.
        """
        pass

    @abstractmethod
    def finalize_assessment(self) -> Dict[str, Any]:
        """Compute aggregate metrics, rep counts, form deviations, scores, and injury insights.

        Returns
        -------
        Dict[str, Any]
            Standardized project assessment schema.
        """
        pass

    @abstractmethod
    def get_hud_state(self, frame_idx: int) -> Dict[str, Any]:
        """Retrieve HUD display state for annotating frame_idx."""
        pass
