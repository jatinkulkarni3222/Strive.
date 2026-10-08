"""STRIVE Video Analysis Pipeline Orchestrator.

Executes the end-to-end Computer Vision pipeline:
1. Video decoding & frame extraction (OpenCV)
2. 33-Landmark Pose detection (MediaPipe)
3. Body-scale normalization (Torso scaling)
4. Temporal smoothing (Savitzky-Golay & EMA)
5. Kinematic derivatives (Velocity & Acceleration)
6. Strategy-based sport biomechanics (Squat, etc.)
7. Video rendering & skeleton HUD annotation
8. Final assessment compilation with injury rules and confidence checks
"""
import os
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from app.core.pose_detector import PoseDetector, NoPersonDetectedError
from app.core.normalizer import BodyScaleNormalizer
from app.core.smoothing import TemporalSmoother
from app.core.biomechanics import compute_kinematics
from app.core.annotator import VideoAnnotator
from app.sports.registry import SportAssessmentFactory
from app.config import (
    ANNOTATED_DIR,
    CONFIDENCE_THRESHOLD_MIN,
    QUALITY_WARNING_THRESHOLD,
    MEDICAL_DISCLAIMER
)


class VideoPipelineError(Exception):
    """Base exception for pipeline failures."""
    pass


class InvalidVideoError(VideoPipelineError):
    """Raised when the video file cannot be decoded."""
    pass


class VideoPipeline:
    """Orchestrates end-to-end video analysis and skeleton rendering."""

    def __init__(self, smoothing_method: str = "savgol"):
        self.pose_detector = PoseDetector(smooth_landmarks=True)
        self.normalizer = BodyScaleNormalizer()
        self.smoother = TemporalSmoother(alpha=0.65, savgol_window=7, savgol_polyorder=2)
        self.smoothing_method = smoothing_method

    def analyze_video(
        self,
        video_path: Path,
        sport_name: str = "squat",
        output_annotated_name: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Path]:
        """Process video and generate biomechanical assessment + annotated video.

        Parameters
        ----------
        video_path : Path
            Path to input video file.
        sport_name : str
            Sport assessment type (e.g., 'squat').
        output_annotated_name : Optional[str]
            Desired filename for annotated output video.

        Returns
        -------
        Tuple[Dict[str, Any], Path]
            assessment_json, annotated_video_path
        """
        if not video_path.exists():
            raise InvalidVideoError(f"Video file does not exist at '{video_path}'")

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise InvalidVideoError(f"Could not open or decode video at '{video_path}'")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0 or np.isnan(fps):
            fps = 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if total_frames <= 0 or width <= 0 or height <= 0:
            cap.release()
            raise InvalidVideoError("Video contains no valid video stream or has zero dimensions.")

        # Instantiate Sport Strategy
        strategy = SportAssessmentFactory.get_strategy(sport_name, fps=fps)

        # PASS 1: Read all frames and extract raw pose landmarks
        raw_frames: List[np.ndarray] = []
        raw_landmarks_list: List[Optional[np.ndarray]] = []
        visibilities_list: List[np.ndarray] = []
        confidences_list: List[float] = []

        valid_pose_frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            raw_frames.append(frame)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            detection = self.pose_detector.process_frame(frame_rgb)

            if detection is not None:
                landmarks_norm, visibilities, conf = detection
                raw_landmarks_list.append(landmarks_norm)
                visibilities_list.append(visibilities)
                confidences_list.append(conf)
                valid_pose_frame_count += 1
            else:
                raw_landmarks_list.append(None)
                visibilities_list.append(np.zeros((33,), dtype=np.float32))
                confidences_list.append(0.0)

        cap.release()

        num_extracted_frames = len(raw_frames)
        if num_extracted_frames == 0:
            raise InvalidVideoError("Video contains 0 readable frames.")

        # Guard against video with no detected humans
        if valid_pose_frame_count == 0 or (valid_pose_frame_count / num_extracted_frames) < 0.15:
            raise NoPersonDetectedError(
                f"No athlete detected in video ({valid_pose_frame_count}/{num_extracted_frames} frames with pose). "
                "Ensure the athlete is in full view with adequate lighting."
            )

        # Interpolate missing frames to maintain continuous kinematics
        # Find first valid frame
        first_valid_idx = next(i for i, lm in enumerate(raw_landmarks_list) if lm is not None)
        filled_landmarks = np.zeros((num_extracted_frames, 33, 3), dtype=np.float32)
        filled_visibilities = np.zeros((num_extracted_frames, 33), dtype=np.float32)

        last_valid = raw_landmarks_list[first_valid_idx]
        last_vis = visibilities_list[first_valid_idx]

        for i in range(num_extracted_frames):
            if raw_landmarks_list[i] is not None:
                last_valid = raw_landmarks_list[i]
                last_vis = visibilities_list[i]
            filled_landmarks[i] = last_valid
            filled_visibilities[i] = last_vis

        # Step 3: Body-scale normalization across sequence
        normalized_sequence = self.normalizer.normalize_sequence(filled_landmarks)

        # Step 4: Temporal smoothing (Savitzky-Golay / EMA)
        smoothed_sequence = self.smoother.smooth(normalized_sequence, method=self.smoothing_method)

        # Step 5: Kinematics (Velocity & Acceleration on normalized coordinates)
        velocities, accelerations = compute_kinematics(smoothed_sequence, fps=fps)

        # Step 6 & 7: Feed frames through Sport Strategy
        for i in range(num_extracted_frames):
            timestamp = i / fps
            strategy.process_frame(
                frame_idx=i,
                timestamp=timestamp,
                landmarks_norm=smoothed_sequence[i],
                visibilities=filled_visibilities[i],
                frame_confidence=confidences_list[i]
            )

        # Finalize assessment
        assessment = strategy.finalize_assessment()

        # Overall landmark confidence score (Equation 1.9.8)
        avg_confidence = float(np.mean(confidences_list))
        quality_warning = None
        if avg_confidence < QUALITY_WARNING_THRESHOLD:
            quality_warning = (
                f"Average landmark confidence ({avg_confidence:.0%}) is below recommended threshold ({QUALITY_WARNING_THRESHOLD:.0%}). "
                "Video may have low lighting, motion blur, or partial occlusion."
            )

        assessment["confidence_score"] = round(avg_confidence, 2)
        assessment["quality_warning"] = quality_warning
        assessment["total_frames_analyzed"] = num_extracted_frames
        assessment["duration_seconds"] = round(num_extracted_frames / fps, 2)
        assessment["fps"] = round(fps, 1)

        # Render Annotated Video
        if not output_annotated_name:
            output_annotated_name = f"annotated_{video_path.stem}.mp4"

        output_video_path = ANNOTATED_DIR / output_annotated_name
        annotator = VideoAnnotator(fps=fps)

        # FourCC for MP4
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(output_video_path), fourcc, fps, (width, height))

        for i in range(num_extracted_frames):
            frame = raw_frames[i]
            hud = strategy.get_hud_state(i)

            # Convert normalized landmarks to pixel coords for drawing
            lm_pix = np.zeros((33, 2), dtype=np.float32)
            lm_pix[:, 0] = filled_landmarks[i, :, 0] * width
            lm_pix[:, 1] = filled_landmarks[i, :, 1] * height

            # Highlight knees & hips for squat
            highlight_joints = [23, 24, 25, 26]

            # Draw skeleton
            frame = annotator.draw_skeleton(
                frame,
                lm_pix,
                filled_visibilities[i],
                highlight_joints=highlight_joints
            )

            # Draw HUD
            frame = annotator.draw_hud(
                frame,
                rep_count=hud["rep_count"],
                primary_angle=hud["knee_angle"],
                angle_name="Knee",
                secondary_angle=hud["torso_lean"],
                sec_angle_name="Lean",
                active_warning=hud.get("active_warning"),
                phase=hud.get("phase", "standing"),
                confidence=hud.get("confidence", 1.0)
            )

            writer.write(frame)

        writer.release()
        assessment["annotated_video_filename"] = output_video_path.name

        return assessment, output_video_path

    def close(self):
        self.pose_detector.close()
