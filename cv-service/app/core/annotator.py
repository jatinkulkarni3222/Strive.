"""Video Skeleton and Biomechanical HUD Annotator Module.

Renders pose skeletons, real-time joint angles, repetition counts,
instantaneous form feedback, and medical disclaimers onto video frames using OpenCV.
"""
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple, Any


class VideoAnnotator:
    """Overlays biomechanical skeleton, HUD metrics, and warnings onto video frames."""

    # Skeleton connections (MediaPipe landmark pairs)
    SKELETON_PAIRS = [
        # Torso
        (11, 12), (11, 23), (12, 24), (23, 24),
        # Left arm
        (11, 13), (13, 15),
        # Right arm
        (12, 14), (14, 16),
        # Left leg
        (23, 25), (25, 27), (27, 29), (27, 31),
        # Right leg
        (24, 26), (26, 28), (28, 30), (28, 32),
    ]

    # Colors in BGR
    COLOR_PRIMARY = (50, 205, 50)       # Emerald Green
    COLOR_WARNING = (0, 165, 255)       # Amber Orange
    COLOR_DANGER = (0, 0, 230)          # Red
    COLOR_CYAN = (255, 200, 0)          # Cyan/Blue
    COLOR_BG = (20, 20, 20)             # Charcoal Black
    COLOR_WHITE = (255, 255, 255)

    def __init__(self, fps: float = 30.0):
        self.fps = fps

    def draw_hud(
        self,
        frame: np.ndarray,
        rep_count: int,
        primary_angle: float,
        angle_name: str,
        secondary_angle: Optional[float] = None,
        sec_angle_name: Optional[str] = None,
        active_warning: Optional[str] = None,
        phase: str = "standing",
        confidence: float = 1.0
    ) -> np.ndarray:
        """Render HUD metrics panel and disclaimer."""
        h, w, _ = frame.shape

        # Semi-transparent top HUD bar
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 85), self.COLOR_BG, -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        # Rep Counter Card (top-left)
        cv2.putText(
            frame, f"REPS: {rep_count}", (20, 42),
            cv2.FONT_HERSHEY_DUPLEX, 1.1, self.COLOR_PRIMARY, 2, cv2.LINE_AA
        )
        cv2.putText(
            frame, f"PHASE: {phase.upper()}", (20, 72),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA
        )

        # Joint Angles (top-center/right)
        angle_text = f"{angle_name}: {primary_angle:.1f} deg"
        cv2.putText(
            frame, angle_text, (w // 2 - 100, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.75, self.COLOR_WHITE, 2, cv2.LINE_AA
        )
        if secondary_angle is not None and sec_angle_name:
            sec_text = f"{sec_angle_name}: {secondary_angle:.1f} deg"
            cv2.putText(
                frame, sec_text, (w // 2 - 100, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.60, (180, 220, 255), 1, cv2.LINE_AA
            )

        # Confidence Badge (top-right)
        conf_color = self.COLOR_PRIMARY if confidence >= 0.60 else self.COLOR_WARNING
        cv2.putText(
            frame, f"Track: {confidence:.0%}", (w - 170, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.60, conf_color, 2, cv2.LINE_AA
        )

        # Active Warning Banner (bottom or mid-bottom)
        if active_warning:
            banner_overlay = frame.copy()
            cv2.rectangle(banner_overlay, (0, h - 90), (w, h - 45), self.COLOR_DANGER, -1)
            cv2.addWeighted(banner_overlay, 0.85, frame, 0.15, 0, frame)
            cv2.putText(
                frame, f"ALERT: {active_warning}", (20, h - 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.70, self.COLOR_WHITE, 2, cv2.LINE_AA
            )

        # Mandatory STRIVE Medical Disclaimer bar (very bottom)
        cv2.rectangle(frame, (0, h - 25), (w, h), (10, 10, 10), -1)
        disclaimer_text = "STRIVE Athletic Screening • Not a medical diagnosis"
        cv2.putText(
            frame, disclaimer_text, (20, h - 8),
            cv2.FONT_HERSHEY_SIMPLEX, 0.40, (160, 160, 160), 1, cv2.LINE_AA
        )

        return frame

    def draw_skeleton(
        self,
        frame: np.ndarray,
        landmarks_pixels: np.ndarray,
        visibilities: np.ndarray,
        highlight_joints: Optional[List[int]] = None
    ) -> np.ndarray:
        """Render anatomical skeleton lines and joints onto frame."""
        h, w, _ = frame.shape
        highlight_joints = highlight_joints or []

        # Draw bones
        for start_idx, end_idx in self.SKELETON_PAIRS:
            if (visibilities[start_idx] >= 0.4 and visibilities[end_idx] >= 0.4):
                pt1 = (int(landmarks_pixels[start_idx, 0]), int(landmarks_pixels[start_idx, 1]))
                pt2 = (int(landmarks_pixels[end_idx, 0]), int(landmarks_pixels[end_idx, 1]))
                cv2.line(frame, pt1, pt2, self.COLOR_CYAN, 3, cv2.LINE_AA)

        # Draw joint nodes
        for idx in range(len(landmarks_pixels)):
            if visibilities[idx] >= 0.4:
                pt = (int(landmarks_pixels[idx, 0]), int(landmarks_pixels[idx, 1]))
                if idx in highlight_joints:
                    # Larger glowing ring for focal joints (e.g. knees/hips)
                    cv2.circle(frame, pt, 8, self.COLOR_WARNING, -1, cv2.LINE_AA)
                    cv2.circle(frame, pt, 11, self.COLOR_WHITE, 2, cv2.LINE_AA)
                else:
                    cv2.circle(frame, pt, 5, self.COLOR_PRIMARY, -1, cv2.LINE_AA)

        return frame
