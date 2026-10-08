"""Standalone Test Script for STRIVE Squat Assessment Pipeline.

Loads sample video from /data/samples or strive/data/samples, executes the
full end-to-end Computer Vision pipeline, renders the annotated skeleton video,
and prints the standardized output JSON.
"""
import sys
import json
import argparse
from pathlib import Path

# Add cv-service to python path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from app.core.pipeline import VideoPipeline, VideoPipelineError
from app.config import MEDICAL_DISCLAIMER


def find_sample_video(preferred_path: str = None) -> Path:
    """Resolve sample video location across multiple standard search paths."""
    candidates = []
    if preferred_path:
        candidates.append(Path(preferred_path))

    # Search locations
    candidates.extend([
        Path("/data/samples/sample_squat.mp4"),
        current_dir.parent / "data" / "samples" / "sample_squat.mp4",
        current_dir / "data" / "samples" / "sample_squat.mp4",
        Path.home() / ".gemini" / "antigravity" / "scratch" / "strive" / "data" / "samples" / "sample_squat.mp4"
    ])

    for path in candidates:
        if path.exists() and path.is_file():
            return path

    raise FileNotFoundError(
        f"Sample video not found. Checked candidate paths:\n" +
        "\n".join(f" - {c}" for c in candidates)
    )


def main():
    parser = argparse.ArgumentParser(description="STRIVE Squat CV Pipeline Test Runner")
    parser.add_argument("--video", type=str, default=None, help="Path to sports video")
    parser.add_argument("--sport", type=str, default="squat", help="Sport activity (default: squat)")
    parser.add_argument("--output-json", type=str, default=None, help="Optional path to save output JSON")
    args = parser.parse_args()

    try:
        video_path = find_sample_video(args.video)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"===========================================================", file=sys.stderr)
    print(f"STRIVE BIOMECHANICAL ASSESSMENT PIPELINE", file=sys.stderr)
    print(f"===========================================================", file=sys.stderr)
    print(f"Input Video : {video_path}", file=sys.stderr)
    print(f"Sport Type  : {args.sport}", file=sys.stderr)
    print(f"Processing frames and extracting 33 MediaPipe landmarks...", file=sys.stderr)

    pipeline = VideoPipeline(smoothing_method="savgol")
    try:
        assessment, annotated_path = pipeline.analyze_video(
            video_path=video_path,
            sport_name=args.sport,
            output_annotated_name=f"annotated_{video_path.stem}.mp4"
        )
        assessment["annotated_video_path"] = str(annotated_path)

        print(f"Processing Complete!", file=sys.stderr)
        print(f"Annotated Video Saved: {annotated_path}", file=sys.stderr)
        print(f"===========================================================\n", file=sys.stderr)

        json_output = json.dumps(assessment, indent=2)

        if args.output_json:
            out_file = Path(args.output_json)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with open(out_file, "w") as f:
                f.write(json_output)
            print(f"Saved JSON to {out_file}", file=sys.stderr)

        # Output JSON to stdout
        print(json_output)

    except VideoPipelineError as e:
        print(f"Pipeline Execution Failed: {e}", file=sys.stderr)
        sys.exit(2)
    finally:
        pipeline.close()


if __name__ == "__main__":
    main()
