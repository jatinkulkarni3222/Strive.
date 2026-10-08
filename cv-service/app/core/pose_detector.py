"""MediaPipe Pose Landmark Detector Module.

Detects 33 body landmarks, tracks confidence visibility (Equation 1.9.8),
and handles detection failures gracefully.
"""
import numpy as np
from typing import Optional, Tuple, List, Dict, Any


class PoseDetectionError(Exception):
    """Raised when pose detection fails critically."""
    pass


class NoPersonDetectedError(PoseDetectionError):
    """Raised when no human subject is detected in the video."""
    pass


class PoseDetector:
    """Encapsulates MediaPipe Pose estimation and confidence metric extraction."""

    LANDMARK_NAMES = [
        "nose", "left_eye_inner", "left_eye", "left_eye_outer",
        "right_eye_inner", "right_eye", "right_eye_outer",
        "left_ear", "right_ear", "mouth_left", "mouth_right",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_pinky", "right_pinky",
        "left_index", "right_index", "left_thumb", "right_thumb",
        "left_hip", "right_hip", "left_knee", "right_knee",
        "left_ankle", "right_ankle", "left_heel", "right_heel",
        "left_foot_index", "right_foot_index"
    ]

    def __init__(
        self,
        static_image_mode: bool = False,
        model_complexity: int = 1,
        smooth_landmarks: bool = True,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5
    ):
        import mediapipe as mp
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def process_frame(
        self, frame_rgb: np.ndarray
    ) -> Optional[Tuple[np.ndarray, np.ndarray, float]]:
        """Process a single RGB frame and extract landmark coordinates.

        Parameters
        ----------
        frame_rgb : np.ndarray
            RGB image array of shape (H, W, 3).

        Returns
        -------
        Optional[Tuple[np.ndarray, np.ndarray, float]]
            landmarks_norm: np.ndarray shape (33, 3) with [x, y, z] in normalized [0, 1] space.
            visibilities: np.ndarray shape (33,) with detection confidence scores c_i.
            frame_confidence: float mean visibility score across 33 keypoints.
            Returns None if no human body is detected.
        """
        results = self.pose.process(frame_rgb)
        if not results.pose_landmarks:
            return None

        raw_landmarks = results.pose_landmarks.landmark
        landmarks_norm = np.zeros((33, 3), dtype=np.float32)
        visibilities = np.zeros((33,), dtype=np.float32)

        for i, lm in enumerate(raw_landmarks):
            landmarks_norm[i] = [lm.x, lm.y, lm.z]
            visibilities[i] = getattr(lm, "visibility", 1.0)

        # Equation (1.9.8): C = (1 / N) * sum(c_i)
        frame_confidence = float(np.mean(visibilities))
        return landmarks_norm, visibilities, frame_confidence

    def close(self):
        """Release MediaPipe resources."""
        if hasattr(self, "pose") and self.pose:
            self.pose.close()
