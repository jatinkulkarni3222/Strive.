"""STRIVE CV Service Configuration.

Defines reference ranges for good form, scoring feature weights,
confidence thresholds, and standardized injury-prevention rules.
"""
from pathlib import Path
from typing import Dict, Any

# Base Storage Paths
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
ANNOTATED_DIR = STORAGE_DIR / "annotated"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)

# Quality & Confidence Settings
CONFIDENCE_THRESHOLD_MIN = 0.50
QUALITY_WARNING_THRESHOLD = 0.60

# Universal Medical Disclaimer
MEDICAL_DISCLAIMER = (
    "STRIVE biomechanical feedback and injury-risk insights are designed for athletic "
    "performance enhancement, technique optimization, and screening only. Not a medical diagnosis."
)

# Sport-Specific Biomechanical Form References & Scoring Weights
SPORT_CONFIGS: Dict[str, Dict[str, Any]] = {
    "squat": {
        "display_name": "Bodyweight / Back Squat",
        "description": "Lower-body bilateral movement assessing knee/hip flexion and spinal stability.",
        # Ideal angles in degrees at the bottom of the movement (inflection point)
        "reference_form": {
            "knee_angle_bottom_min": 70.0,
            "knee_angle_bottom_max": 100.0,  # Parallel or slightly below parallel
            "hip_angle_bottom_min": 75.0,
            "hip_angle_bottom_max": 105.0,
            "torso_lean_max_deg": 35.0,       # Max forward lean relative to vertical (ideal <= 35)
            "knee_valgus_ratio_min": 0.85,    # (knee_distance / ankle_distance) >= 0.85
            "spine_angle_deviation_max": 20.0 # Curvature deviation
        },
        # Repetition State Machine Thresholds
        "rep_thresholds": {
            "standing_knee_angle": 160.0,     # Fully extended standing
            "descent_knee_angle": 125.0,      # Entering descent
            "bottom_knee_angle": 100.0,       # Reaching valid squat depth
            "min_rep_duration_sec": 0.8,      # Filter false twitches
            "max_rep_duration_sec": 7.0
        },
        # Scoring Weights (w_i sum to 1.0)
        "scoring_weights": {
            "depth_rom": 0.35,                # Range of motion at bottom
            "form_deviation": 0.35,           # Angular adherence to reference good form
            "rep_consistency": 0.20,          # Uniformity across repetitions
            "kinematic_stability": 0.10       # Smoothness of velocity & acceleration
        }
    },
    "pushup": {
        "display_name": "Push-Up",
        "description": "Upper-body horizontal pressing assessing core stability and shoulder/elbow mechanics.",
        "reference_form": {
            "elbow_angle_bottom_min": 70.0,
            "elbow_angle_bottom_max": 95.0,
            "trunk_alignment_min": 160.0,     # Shoulder-hip-ankle line (neutral plank)
            "trunk_alignment_max": 185.0,
            "elbow_flare_max_deg": 75.0       # Angle between arm and torso
        },
        "rep_thresholds": {
            "top_elbow_angle": 155.0,
            "bottom_elbow_angle": 95.0,
            "min_rep_duration_sec": 0.7,
            "max_rep_duration_sec": 6.0
        },
        "scoring_weights": {
            "rom": 0.35,
            "form_deviation": 0.35,
            "rep_consistency": 0.20,
            "kinematic_stability": 0.10
        }
    },
    "vertical_jump": {
        "display_name": "Vertical Jump",
        "description": "Explosive triple extension assessing countermovement, vertical displacement, and landing stability.",
        "reference_form": {
            "countermovement_knee_min": 80.0,
            "countermovement_knee_max": 115.0,
            "takeoff_symmetry_ratio": 0.90,
            "landing_valgus_ratio_min": 0.85
        },
        "scoring_weights": {
            "jump_height_displacement": 0.50,
            "takeoff_velocity": 0.25,
            "landing_mechanics": 0.25
        }
    }
}
