"""STRIVE Computer Vision Service - FastAPI Application.

Exposes REST endpoints for video upload and biomechanical assessment:
- POST /analyze (video + sport) -> JSON assessment + annotated video URL
- GET /health -> Service status & supported sports
- GET /annotated/{filename} -> Stream/download annotated skeleton video
"""
import shutil
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.pipeline import VideoPipeline, InvalidVideoError, NoPersonDetectedError
from app.sports.registry import SportAssessmentFactory
from app.config import UPLOAD_DIR, ANNOTATED_DIR, MEDICAL_DISCLAIMER

app = FastAPI(
    title="STRIVE Computer Vision Assessment API",
    description="Accessible smartphone-based sports talent assessment and biomechanical analysis.",
    version="1.0.0"
)

# Enable CORS for frontend and backend proxies
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supported video extensions
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".webm", ".m4v"}
MAX_FILE_SIZE_BYTES = 150 * 1024 * 1024  # 150 MB limit


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Health check returning service status and supported assessment modules."""
    return {
        "status": "UP",
        "service": "strive-cv-service",
        "supported_sports": SportAssessmentFactory.supported_sports(),
        "disclaimer": MEDICAL_DISCLAIMER
    }


@app.post("/analyze", tags=["Assessment"])
async def analyze_video(
    video: UploadFile = File(..., description="Smartphone-captured sports movement video"),
    sport: str = Form("squat", description="Sport assessment type: squat, pushup, vertical_jump")
) -> Dict[str, Any]:
    """Analyze sports video for repetitions, posture deviations, injury risks, and performance score."""
    sport_key = sport.strip().lower()
    if sport_key not in SportAssessmentFactory.supported_sports():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported sport '{sport}'. Supported options: {SportAssessmentFactory.supported_sports()}"
        )

    file_suffix = Path(video.filename or "video.mp4").suffix.lower()
    if file_suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension '{file_suffix}'. Allowed formats: {sorted(list(ALLOWED_EXTENSIONS))}"
        )

    # Save uploaded video
    session_id = uuid.uuid4().hex[:10]
    safe_filename = f"{session_id}_{video.filename}"
    upload_path = UPLOAD_DIR / safe_filename
    annotated_filename = f"annotated_{session_id}.mp4"

    try:
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded video: {str(e)}"
        )

    # Check file size
    if upload_path.stat().st_size > MAX_FILE_SIZE_BYTES:
        upload_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file exceeds maximum allowed limit of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB."
        )

    # Run analysis pipeline
    pipeline = VideoPipeline()
    try:
        assessment, annotated_path = pipeline.analyze_video(
            video_path=upload_path,
            sport_name=sport_key,
            output_annotated_name=annotated_filename
        )
    except NoPersonDetectedError as e:
        upload_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except InvalidVideoError as e:
        upload_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        upload_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Biomechanical analysis failed: {str(e)}"
        )
    finally:
        pipeline.close()

    # Build response payload
    assessment["annotated_video_url"] = f"/annotated/{annotated_filename}"
    assessment["raw_video_filename"] = safe_filename

    return assessment


@app.get("/annotated/{filename}", tags=["Media"])
async def get_annotated_video(filename: str):
    """Stream or download processed video with skeletal HUD overlay."""
    file_path = ANNOTATED_DIR / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotated video file not found."
        )
    return FileResponse(
        path=str(file_path),
        media_type="video/mp4",
        filename=filename
    )
