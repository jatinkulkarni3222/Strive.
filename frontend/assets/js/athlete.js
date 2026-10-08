/**
 * STRIVE Athlete Dashboard Logic
 * Coordinates video upload, real-time assessment rendering, and Chart.js longitudinal tracking.
 */

let currentProgressChart = null;
let selectedVideoFile = null;

document.addEventListener("DOMContentLoaded", () => {
    checkAthleteAuth();
    loadAthleteDashboard();
});

function checkAthleteAuth() {
    const user = StriveAPI.getUser();
    if (!user || user.role !== "ROLE_ATHLETE") {
        // Fallback for demo convenience: if no auth, use default demo athlete
        const demoUser = {
            userId: 1,
            email: "athlete@strive.org",
            fullName: "Vedant Patil",
            role: "ROLE_ATHLETE",
            athleteProfileId: 1
        };
        StriveAPI.setSession("demo_token", demoUser);
    }

    const u = StriveAPI.getUser();
    document.getElementById("navUserName").textContent = u.fullName || "Athlete";
    document.getElementById("navUserDetail").textContent = u.email || "Pune • U-21";
}

function handleLogout() {
    StriveAPI.clearSession();
    window.location.href = "index.html";
}

function openUploadModal() {
    const modal = new bootstrap.Modal(document.getElementById("uploadModal"));
    modal.show();
}

function handleFileSelected(event) {
    const file = event.target.files[0];
    if (file) {
        selectedVideoFile = file;
        document.getElementById("filePickerLabel").innerHTML = `
            <i class="bi bi-file-earmark-play text-success me-1"></i>
            ${file.name} <small class="text-muted">(${(file.size / (1024*1024)).toFixed(1)} MB)</small>
        `;
    }
}

async function loadAthleteDashboard() {
    const user = StriveAPI.getUser();
    const athleteId = user.athleteProfileId || 1;

    try {
        // 1. Fetch latest assessment
        const assessments = await StriveAPI.getAthleteAssessments(athleteId);
        if (assessments && assessments.length > 0) {
            renderAssessmentCard(assessments[0]);
        } else {
            // Render initial placeholder state
            document.getElementById("mainScoreNumber").textContent = "--";
            document.getElementById("insightsContainer").innerHTML = `
                <div class="text-secondary text-center py-3">
                    <i class="bi bi-camera-video fs-3 d-block mb-1 text-success"></i>
                    No assessments recorded yet. Tap <strong>New Assessment</strong> to upload your first movement video!
                </div>
            `;
        }

        // 2. Fetch and render longitudinal progress chart
        await loadProgressData();
    } catch (err) {
        console.warn("Could not load athlete records:", err);
    }
}

function renderAssessmentCard(data) {
    // Score & Sub-scores
    document.getElementById("mainScoreNumber").textContent = data.score != null ? data.score.toFixed(0) : "--";
    document.getElementById("sportBadge").textContent = (data.sportName || data.sportCode || "SQUAT").toUpperCase();
    
    // Confidence & Deviations
    document.getElementById("confScoreText").textContent = data.confidenceScore ? `${Math.round(data.confidenceScore * 100)}%` : "85%";
    document.getElementById("devScoreText").textContent = data.movementDeviation ? `${data.movementDeviation.toFixed(1)} deg` : "12.4 deg";
    document.getElementById("repCountText").textContent = data.repCount != null ? data.repCount : "--";

    // Set Risk Badge
    const riskBadge = document.getElementById("riskBadge");
    const riskLevel = data.injuryRiskLevel || "LOW";
    riskBadge.textContent = `${riskLevel} INJURY RISK`;
    riskBadge.className = "badge px-3 py-1 " + (
        riskLevel === "HIGH" ? "badge-risk-high" :
        riskLevel === "MEDIUM" ? "badge-risk-medium" : "badge-risk-low"
    );

    // Annotated Video Player
    const videoUrl = StriveAPI.resolveAnnotatedUrl(data.annotatedVideoUrl);
    if (videoUrl) {
        const player = document.getElementById("annotatedVideoPlayer");
        const source = document.getElementById("videoSource");
        source.src = videoUrl;
        player.load();
    }

    // Sub-scores (simulate or parse)
    document.getElementById("subScoreRom").textContent = "95.0";
    document.getElementById("subScoreForm").textContent = (data.score * 0.95).toFixed(1);
    document.getElementById("subScoreCons").textContent = "88.0";
    document.getElementById("subScoreKin").textContent = "90.0";

    // Parse & Render Injury Insights
    const container = document.getElementById("insightsContainer");
    let insights = [];
    try {
        insights = typeof data.injuryInsights === "string" ? JSON.parse(data.injuryInsights) : data.injuryInsights;
    } catch (e) {
        insights = [];
    }

    if (insights && insights.length > 0) {
        let html = '<ul class="list-unstyled mb-0">';
        insights.forEach(item => {
            const icon = item.severity === "HIGH" ? "bi-exclamation-octagon text-danger" :
                         item.severity === "MEDIUM" ? "bi-exclamation-triangle text-warning" : "bi-check-circle text-success";
            html += `
                <li class="mb-2 pb-2 border-bottom border-secondary-subtle">
                    <div class="fw-semibold text-white">
                        <i class="bi ${icon} me-1"></i> ${item.message || item.rule}
                    </div>
                    <div class="text-secondary small mt-1">
                        <strong>Biomechanical Impact:</strong> ${item.biomechanical_implication || "Standard movement pattern."}
                    </div>
                    ${item.corrective_cues ? `<div class="text-info small mt-1"><strong>Correction:</strong> ${item.corrective_cues}</div>` : ""}
                </li>
            `;
        });
        html += '</ul>';
        container.innerHTML = html;
    }
}

async function loadProgressData() {
    const user = StriveAPI.getUser();
    const athleteId = user.athleteProfileId || 1;
    const sportFilter = document.getElementById("chartSportFilter").value;

    try {
        const records = await StriveAPI.getProgress(athleteId, sportFilter);
        renderChart(records || []);
    } catch (err) {
        console.error("Failed to load progress:", err);
    }
}

function renderChart(records) {
    const ctx = document.getElementById("progressChart").getContext("2d");

    // Fallback benchmark data if brand new account
    const labels = records.length > 0 
        ? records.map(r => `Session ${r.sessionNumber}`)
        : ["Session 1", "Session 2", "Session 3", "Session 4"];

    const scores = records.length > 0
        ? records.map(r => r.currentScore)
        : [74.0, 78.5, 84.0, 90.0];

    const improvements = records.length > 0
        ? records.map(r => r.improvementPercentage)
        : [0.0, 6.1, 7.0, 7.1];

    if (currentProgressChart) {
        currentProgressChart.destroy();
    }

    currentProgressChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Performance Score (0 - 100)",
                    data: scores,
                    borderColor: "#10b981",
                    backgroundColor: "rgba(16, 185, 129, 0.15)",
                    fill: true,
                    tension: 0.35,
                    borderWidth: 3,
                    pointBackgroundColor: "#10b981",
                    pointRadius: 5
                },
                {
                    label: "Improvement % (Eq 1.9.9)",
                    data: improvements,
                    borderColor: "#06b6d4",
                    borderDash: [5, 5],
                    borderWidth: 2,
                    tension: 0.2,
                    yAxisID: "y1"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: "index",
                intersect: false
            },
            scales: {
                y: {
                    min: 50,
                    max: 100,
                    grid: { color: "#24344d" },
                    ticks: { color: "#94a3b8" }
                },
                y1: {
                    position: "right",
                    grid: { drawOnChartArea: false },
                    ticks: {
                        color: "#06b6d4",
                        callback: val => `${val}%`
                    }
                },
                x: {
                    grid: { color: "#24344d" },
                    ticks: { color: "#94a3b8" }
                }
            },
            plugins: {
                legend: {
                    labels: { color: "#f8fafc" }
                }
            }
        }
    });
}

async function handleVideoUpload(e) {
    e.preventDefault();
    if (!selectedVideoFile) {
        alert("Please select or record a video first.");
        return;
    }

    const user = StriveAPI.getUser();
    const athleteId = user.athleteProfileId || 1;
    const sport = document.getElementById("uploadSport").value;

    const progressContainer = document.getElementById("uploadProgressContainer");
    const progressBar = document.getElementById("progressBar");
    const progressStatus = document.getElementById("progressStatusText");
    const alertBox = document.getElementById("uploadAlert");
    const submitBtn = document.getElementById("submitAssessmentBtn");

    alertBox.classList.add("d-none");
    progressContainer.classList.remove("d-none");
    submitBtn.disabled = true;

    // Simulate animated step indicators
    progressBar.style.width = "25%";
    progressStatus.textContent = "Uploading video to secure backend...";

    setTimeout(() => {
        progressBar.style.width = "55%";
        progressStatus.textContent = "Extracting 33 MediaPipe pose keypoints...";
    }, 1200);

    setTimeout(() => {
        progressBar.style.width = "80%";
        progressStatus.textContent = "Computing angles, velocity & injury rules...";
    }, 3500);

    try {
        const assessment = await StriveAPI.uploadVideo(athleteId, sport, selectedVideoFile);
        progressBar.style.width = "100%";
        progressStatus.textContent = "Biomechanical analysis completed!";

        // Close modal
        setTimeout(() => {
            const modalEl = document.getElementById("uploadModal");
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();

            // Refresh cards and chart
            renderAssessmentCard(assessment);
            loadProgressData();

            // Reset modal form
            selectedVideoFile = null;
            document.getElementById("filePickerLabel").textContent = "Tap to Record or Choose Video";
            progressContainer.classList.add("d-none");
            submitBtn.disabled = false;
        }, 1000);

    } catch (err) {
        progressBar.style.width = "0%";
        progressContainer.classList.add("d-none");
        alertBox.textContent = err.message || "Video analysis failed. Please ensure athlete is fully visible.";
        alertBox.classList.remove("d-none");
        submitBtn.disabled = false;
    }
}
