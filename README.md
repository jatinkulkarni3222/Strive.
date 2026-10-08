# STRIVE: Accessible Smartphone-Based Sports Talent Assessment & Longitudinal Development

> **Bachelor of Engineering (Computer Engineering) Capstone Project**  
> **Savitribai Phule Pune University (SPPU) • PCCOER Ravet, Academic Year 2026-27**  
> **Authors:** Vedant Patil, Atharva Jadhav, Aditya Gawande, Jatin Kulkarni  
> **Internal Guide:** Mrs. Rutuja Magar • **H.O.D.:** Dr. Vijay A. Kotkar

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Java 21 / 17](https://img.shields.io/badge/Java-21%20%7C%2017-orange.svg)](https://adoptium.net/)
[![Spring Boot 3](https://img.shields.io/badge/Spring%20Boot-3.2.3-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose%2033%20Landmarks-blueviolet.svg)](https://developers.google.com/mediapipe)
[![Tests](https://img.shields.io/badge/Tests-PyTest%20%2B%20JUnit%205-success.svg)](#testing)

---

## 1. Problem Statement & Motivation

Athletes in rural and underserved regions often lack access to professional sports academies, certified biomechanical coaches, and expensive multi-camera motion-capture labs. Conventional talent discovery relies on manual, infrequent, subjective observation.

**STRIVE** bridges this opportunity gap:
- An athlete records a movement video using any commodity smartphone camera.
- The computer vision engine tracks 33 anatomical landmarks, normalizes coordinates by torso scale, calculates joint kinematics, and counts repetitions using state machine logic.
- Performance scores ($S = \sum w_i f_i$) and rule-based injury prevention warnings (e.g., knee valgus, excessive trunk lean, elbow flare) are computed in seconds.
- Historical assessments establish longitudinal progress ($I = \frac{S_t - S_{t-1}}{S_{t-1}} \times 100$), enabling coaches and scouts to discover emerging talent objectively.

---

## 2. System Architecture

```mermaid
flowchart TD
    subgraph Client["Presentation Tier (Mobile-First Web)"]
        UI_Athlete["Athlete Dashboard\n• Native Camera Capture\n• Biomechanical Scorecards\n• Longitudinal Progress Chart\n• Skeleton Overlay Video Player"]
        UI_Coach["Coach Portal\n• Assigned Athlete Roster\n• Movement Kinematic Review\n• Coaching Feedback Notes"]
        UI_Scout["Scout Portal\n• Grassroots Talent Discovery\n• Multi-Criteria Cohort Filters\n• Athlete Dossier & Verification"]
    end

    subgraph Backend["Application Tier (Spring Boot 3 REST API)"]
        SecFilter["Spring Security + JWT Auth\n(ROLE_ATHLETE, ROLE_COACH, ROLE_SCOUT)"]
        VideoCtrl["Video & Assessment Controller"]
        ProgCtrl["Longitudinal Progress Service\n(I = (St - St-1)/St-1 * 100)"]
        RankCtrl["Cohort Ranking Service\n(Ri = rank(Si))"]
        CoachCtrl["Coach & Scout Services"]
    end

    subgraph CVService["Computer Vision Tier (FastAPI + MediaPipe)"]
        CV_Decode["OpenCV Video Frame Extraction"]
        CV_Pose["MediaPipe BlazePose\n(33 3D Body Landmarks)"]
        CV_Norm["Body-Scale Normalization\n(p' = (p - pc)/s)"]
        CV_Smooth["Savitzky-Golay & EMA Smoothing\n(p^t = a*pt + (1-a)*p^t-1)"]
        CV_Kin["Kinematics & Angles\n(theta = arccos(BA.BC / |BA||BC|))"]
        CV_Sports["Sport Strategies (Plugin Pattern)\n• Squat (Depth, Valgus, Trunk Lean)\n• Push-up (Elbow, Alignment, Flare)\n• Vertical Jump (Displacement, Landing)"]
        CV_Annotate["OpenCV Video Annotator\n(Skeleton Bones, HUD Metrics, Disclaimer)"]
    end

    subgraph Data["Persistence Tier"]
        Postgres[("PostgreSQL 16 Database\n(Users, Profiles, Videos, Assessments,\nFeatureSets, Progress, Rankings)")]
        Storage[("Local / Cloud Storage\n• Raw Uploads\n• Annotated MP4s")]
    end

    UI_Athlete -->|Multipart Video Upload| SecFilter
    UI_Coach -->|REST / JWT| SecFilter
    UI_Scout -->|REST / JWT| SecFilter

    SecFilter --> VideoCtrl
    SecFilter --> ProgCtrl
    SecFilter --> RankCtrl
    SecFilter --> CoachCtrl

    VideoCtrl -->|Forward Video| CV_Decode
    CV_Decode --> CV_Pose --> CV_Norm --> CV_Smooth --> CV_Kin --> CV_Sports --> CV_Annotate
    CV_Annotate -->|Annotated MP4| Storage
    CV_Sports -->|Assessment JSON| VideoCtrl

    VideoCtrl --> Postgres
    ProgCtrl --> Postgres
    RankCtrl --> Postgres
```

---

## 3. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    User ||--o| AthleteProfile : "has profile"
    User ||--o{ CoachAthleteMapping : "mentors as coach"
    AthleteProfile ||--o{ CoachAthleteMapping : "coached by"
    AthleteProfile ||--o{ Video : "uploads"
    SportsActivity ||--o{ Video : "categorizes"
    Video ||--|| Assessment : "evaluated into"
    Assessment ||--|| FeatureSet : "extracts"
    AthleteProfile ||--o{ ProgressRecord : "tracks over time"
    SportsActivity ||--o{ ProgressRecord : "progress in"
    AthleteProfile ||--o{ Ranking : "ranked in"
    SportsActivity ||--o{ Ranking : "leaderboard for"

    User {
        bigint id PK
        varchar email UK
        varchar password
        varchar fullName
        varchar role "ATHLETE, COACH, SCOUT"
        timestamp createdAt
    }

    AthleteProfile {
        bigint id PK
        bigint user_id FK
        date dateOfBirth
        varchar gender
        double heightCm
        double weightKg
        varchar city
        varchar state
        varchar primarySport
    }

    SportsActivity {
        bigint id PK
        varchar code UK "SQUAT, PUSHUP, VERTICAL_JUMP"
        varchar name
        varchar description
    }

    Video {
        bigint id PK
        bigint athlete_id FK
        bigint sports_activity_id FK
        varchar originalFilename
        varchar storagePath
        varchar annotatedPath
        double durationSeconds
        double fps
        varchar status "UPLOADED, ANALYZED, FAILED"
        timestamp uploadedAt
    }

    Assessment {
        bigint id PK
        bigint video_id FK
        bigint athlete_id FK
        bigint sports_activity_id FK
        double score
        double confidenceScore
        double movementDeviation
        int repCount
        varchar injuryRiskLevel "LOW, MEDIUM, HIGH"
        text injuryInsights
        timestamp assessedAt
    }

    FeatureSet {
        bigint id PK
        bigint assessment_id FK
        double avgRom
        double consistencyScore
        double peakVelocity
        double peakAcceleration
        text featureVectorJson
    }

    ProgressRecord {
        bigint id PK
        bigint athlete_id FK
        bigint sports_activity_id FK
        int sessionNumber
        double currentScore
        double previousScore
        double improvementPercentage
        timestamp recordedAt
    }

    Ranking {
        bigint id PK
        bigint athlete_id FK
        bigint sports_activity_id FK
        double normalizedScore
        int rankPosition
        varchar ageGroup "U-17, U-21, SENIOR"
        varchar gender
        timestamp updatedAt
    }

    CoachAthleteMapping {
        bigint id PK
        bigint coach_id FK
        bigint athlete_id FK
        text feedbackNotes
        timestamp assignedAt
    }
```

---

## 4. Mathematical Formulations

### 4.1 Joint Angle Calculation (Equation 1.9.1)
The anatomical joint angle formed at vertex $B$ by connecting segments from landmarks $A$ and $C$:
$$\theta = \arccos\left(\frac{(A - B) \cdot (C - B)}{\|A - B\| \, \|C - B\|}\right)$$

### 4.2 Velocity and Acceleration (Equation 1.9.2)
Keypoint kinematics across time frames with sampling step $\Delta t = \frac{1}{\text{fps}}$:
$$v_t = \frac{p_t - p_{t-1}}{\Delta t}, \quad a_t = \frac{v_t - v_{t-1}}{\Delta t}$$

### 4.3 Body-Scale Normalization (Equation 1.9.3)
Removes camera distance and athlete height variance using torso length $s = \|\text{mid\_shoulder} - \text{mid\_hip}\|$:
$$p'_i = \frac{p_i - p_c}{s}$$

### 4.4 Temporal Smoothing (Equation 1.9.4)
Exponential Moving Average and Savitzky-Golay polynomial filtering to suppress keypoint jitter:
$$\hat{p}_t = \alpha p_t + (1 - \alpha) \hat{p}_{t-1}$$

### 4.5 Performance Assessment Scoring (Equation 1.9.6)
Weighted sum of normalized kinematic features:
$$S = \sum_{i=1}^n w_i f_i \quad \text{subject to} \quad \sum_{i=1}^n w_i = 1$$
*(Weights defined in `app/config.py`: ROM 35%, Form Adherence 35%, Consistency 20%, Stability 10%)*

### 4.6 Movement Deviation (Equation 1.9.7)
Mean absolute distance from reference good form:
$$D = \frac{1}{N}\sum_{i=1}^N |x_i - \hat{x}_i|$$

### 4.7 Longitudinal Performance Improvement (Equation 1.9.9)
Percentage score change across consecutive assessment sessions:
$$I = \frac{S_t - S_{t-1}}{S_{t-1}} \times 100$$

### 4.8 Accuracy Evaluation Metrics (Equations 1.9.11 & 1.9.12)
Validation against ground-truth labels:
$$\text{MAE} = \frac{1}{N}\sum_{i=1}^N |y_i - \hat{y}_i|, \quad \text{RMSE} = \sqrt{\frac{1}{N}\sum_{i=1}^N (y_i - \hat{y}_i)^2}$$

---

## 5. Quickstart & Setup Guide

### Option A: Complete System with Docker Compose (Recommended)

```bash
# Clone and enter directory
cd /Users/jatinpadmakarkulkarni/.gemini/antigravity/scratch/strive

# Launch PostgreSQL, CV Service, Spring Boot Backend, and Frontend Nginx
docker-compose up --build
```
- **Frontend Dashboard:** http://localhost:3000
- **Spring Boot Backend:** http://localhost:8080
- **Swagger / OpenAPI Documentation:** http://localhost:8080/swagger-ui.html
- **CV Service FastAPI:** http://localhost:8000/docs

---

### Option B: Local Development Setup

#### 1. Computer Vision Service (`cv-service`)
```bash
cd cv-service
# Activate virtual environment
source venv/bin/activate

# Run PyTest test suite (21 unit tests)
pytest tests/ -v

# Run the end-to-end sample assessment test script
python test_squat_pipeline.py --video ../data/samples/sample_squat.mp4

# Run ground-truth accuracy benchmark evaluation (MAE & RMSE)
python evaluation/evaluate.py

# Launch FastAPI development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Spring Boot 3 Backend (`backend`)
```bash
cd backend
export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home

# Run Maven tests (JUnit 5 + Mockito)
./mvnw test

# Run Spring Boot application
./mvnw spring-boot:run
```

#### 3. Mobile-First Frontend (`frontend`)
The frontend is built with vanilla HTML5, CSS3, and JavaScript (Bootstrap 5.3 + Chart.js) with no build tools required. Open `frontend/index.html` in any modern desktop or smartphone browser, or serve it using Python's static server:
```bash
cd frontend
python3 -m http.server 3000
```

---

## 6. Pre-Configured Demo Accounts

| Role | Email | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **ATHLETE** | `athlete@strive.org` | `Strive@2026` | Camera capture, scorecards, skeleton replay, longitudinal charts |
| **COACH** | `coach@strive.org` | `Strive@2026` | Assigned athlete monitoring, session inspection, feedback submission |
| **SCOUT** | `scout@strive.org` | `Strive@2026` | Talent search, cohort leaderboards, multi-criteria filtering, dossiers |

---

## 7. Testing & Verification

### PyTest Suite Results (`cv-service`)
```text
tests/test_api.py::test_health_endpoint PASSED                           [  4%]
tests/test_api.py::test_analyze_unsupported_sport PASSED                 [  9%]
tests/test_api.py::test_analyze_invalid_file_extension PASSED            [ 14%]
tests/test_biomechanics.py::test_compute_angle_90_degrees PASSED         [ 19%]
tests/test_biomechanics.py::test_compute_angle_180_straight_line PASSED  [ 23%]
tests/test_biomechanics.py::test_compute_angle_45_degrees PASSED         [ 28%]
tests/test_biomechanics.py::test_compute_angle_3d_coordinates PASSED     [ 33%]
tests/test_biomechanics.py::test_compute_angle_zero_length_fallback PASSED [ 38%]
tests/test_biomechanics.py::test_compute_vector_angle_to_vertical PASSED [ 42%]
tests/test_biomechanics.py::test_compute_kinematics PASSED               [ 47%]
tests/test_biomechanics.py::test_compute_movement_deviation PASSED       [ 52%]
tests/test_normalizer.py::test_body_scale_normalization_scale_invariance PASSED [ 57%]
tests/test_other_sports.py::test_pushup_rep_and_form PASSED              [ 61%]
tests/test_other_sports.py::test_pushup_elbow_flare_rule PASSED          [ 66%]
tests/test_other_sports.py::test_vertical_jump_mechanics PASSED          [ 71%]
tests/test_smoothing.py::test_ema_smoothing_formula PASSED               [ 76%]
tests/test_smoothing.py::test_savgol_smoothing_suppresses_noise PASSED   [ 80%]
tests/test_smoothing.py::test_smoothing_fallback_on_short_sequence PASSED [ 85%]
tests/test_squat.py::test_squat_rep_counting_and_high_score PASSED       [ 90%]
tests/test_squat.py::test_squat_knee_valgus_rule_detection PASSED        [ 95%]
tests/test_squat.py::test_squat_excessive_forward_lean_rule PASSED       [100%]
============================== 21 passed in 3.34s ==============================
```

### Accuracy Evaluation Results (`evaluate.py`)
```text
STRIVE BENCHMARK EVALUATION RESULTS:
--------------------------------------------------
Repetition Counting MAE  (Eq. 1.9.11) : 0.111 reps
Repetition Counting RMSE (Eq. 1.9.12) : 0.333 reps
Performance Score MAE    (Eq. 1.9.11) : 1.411 points
Performance Score RMSE   (Eq. 1.9.12) : 1.747 points
--------------------------------------------------
```

### JUnit 5 Suite Results (`backend`)
```text
[INFO] Running com.strive.service.ProgressServiceTest
[INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running com.strive.service.RankingServiceTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running com.strive.service.AuthServiceTest
[INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
```

---

## 8. Medical & Legal Disclaimer

> **IMPORTANT:** STRIVE biomechanical analysis, joint kinematic calculations, posture deviation indices, and injury-risk insights are designed solely for athletic training optimization, technique screening, and performance development. **STRIVE is not a medical device, nor does it provide medical diagnosis or therapeutic treatment.**
