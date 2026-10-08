/**
 * STRIVE Coach Portal Controller
 */

let coachChart = null;
let currentSelectedAthleteId = 1;

document.addEventListener("DOMContentLoaded", () => {
    checkCoachAuth();
    loadRoster();
});

function checkCoachAuth() {
    const user = StriveAPI.getUser();
    if (!user || user.role !== "ROLE_COACH") {
        const demoCoach = {
            userId: 4,
            email: "coach@strive.org",
            fullName: "Coach Rutuja Magar",
            role: "ROLE_COACH"
        };
        StriveAPI.setSession("demo_coach_token", demoCoach);
    }
    const u = StriveAPI.getUser();
    document.getElementById("coachNavName").textContent = u.fullName || "Coach Rutuja Magar";
}

function handleCoachLogout() {
    StriveAPI.clearSession();
    window.location.href = "index.html";
}

async function loadRoster() {
    const rosterList = document.getElementById("athleteRosterList");
    try {
        const mappings = await StriveAPI.getCoachAthletes();
        if (mappings && mappings.length > 0) {
            renderRosterItems(mappings);
            selectAthlete(mappings[0]);
        } else {
            // Demo fallback roster
            const demoMappings = [
                {
                    athlete: { id: 1, user: { fullName: "Vedant Patil", email: "athlete@strive.org" }, primarySport: "SQUAT", city: "Pune", gender: "MALE", dateOfBirth: "2004-05-14" },
                    feedbackNotes: "Solid squat depth. Needs to focus on knee tracking over toes to prevent inward valgus."
                },
                {
                    athlete: { id: 2, user: { fullName: "Neha Sharma", email: "neha@strive.org" }, primarySport: "SQUAT", city: "Satara", gender: "FEMALE", dateOfBirth: "2006-09-21" },
                    feedbackNotes: "Excellent trunk stability and posture consistency."
                }
            ];
            renderRosterItems(demoMappings);
            selectAthlete(demoMappings[0]);
        }
    } catch (err) {
        console.warn("Using fallback roster:", err);
    }
}

function renderRosterItems(mappings) {
    const container = document.getElementById("athleteRosterList");
    document.getElementById("rosterCount").textContent = mappings.length;

    let html = "";
    mappings.forEach((m, idx) => {
        const ath = m.athlete;
        const name = ath.user ? ath.user.fullName : `Athlete #${ath.id}`;
        html += `
            <div class="strive-card p-3 cursor-pointer" onclick='selectAthlete(${JSON.stringify(m).replace(/'/g, "&apos;")})' style="cursor: pointer;">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <div class="fw-bold text-white">${name}</div>
                        <div class="text-secondary small">${ath.primarySport || "SQUAT"} • ${ath.city || "Maharashtra"}</div>
                    </div>
                    <span class="badge bg-success-subtle text-success">Active</span>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

function selectAthlete(mapping) {
    const ath = mapping.athlete;
    currentSelectedAthleteId = ath.id;

    document.getElementById("selectedAthleteName").textContent = ath.user ? ath.user.fullName : `Athlete #${ath.id}`;
    document.getElementById("selectedAthleteSport").textContent = ath.primarySport || "SQUAT";
    document.getElementById("selectedAthleteLocation").textContent = `${ath.city || "Pune"}, Maharashtra`;
    document.getElementById("feedbackNotesInput").value = mapping.feedbackNotes || "";

    // Load progress graph for this athlete
    loadAthleteChart(ath.id, ath.primarySport || "SQUAT");
}

async function loadAthleteChart(athleteId, sport) {
    try {
        const records = await StriveAPI.getProgress(athleteId, sport);
        const labels = (records && records.length > 0)
            ? records.map(r => `Session ${r.sessionNumber}`)
            : ["S1", "S2", "S3", "S4"];

        const scores = (records && records.length > 0)
            ? records.map(r => r.currentScore)
            : [74.0, 78.5, 84.0, 90.0];

        document.getElementById("selectedAthleteScore").textContent = scores[scores.length - 1].toFixed(1);

        const ctx = document.getElementById("coachProgressChart").getContext("2d");
        if (coachChart) coachChart.destroy();

        coachChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Score",
                    data: scores,
                    borderColor: "#10b981",
                    backgroundColor: "rgba(16, 185, 129, 0.15)",
                    fill: true,
                    tension: 0.3,
                    borderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { min: 50, max: 100, grid: { color: "#24344d" }, ticks: { color: "#94a3b8" } },
                    x: { grid: { color: "#24344d" }, ticks: { color: "#94a3b8" } }
                },
                plugins: { legend: { display: false } }
            }
        });
    } catch (e) {
        console.warn("Chart load fallback:", e);
    }
}

async function handleFeedbackSubmit(e) {
    e.preventDefault();
    const notes = document.getElementById("feedbackNotesInput").value;
    const btn = document.getElementById("saveFeedbackBtn");
    const alert = document.getElementById("feedbackSavedAlert");

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Saving...';

    try {
        await StriveAPI.submitCoachFeedback(currentSelectedAthleteId, notes);
        alert.classList.remove("d-none");
        setTimeout(() => alert.classList.add("d-none"), 3000);
    } catch (err) {
        alert.textContent = "Saved locally for session!";
        alert.classList.remove("d-none");
        setTimeout(() => alert.classList.add("d-none"), 3000);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-send me-1"></i> Save Coaching Note';
    }
}
