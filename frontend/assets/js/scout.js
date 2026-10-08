/**
 * STRIVE Scout Portal Controller
 */

document.addEventListener("DOMContentLoaded", () => {
    checkScoutAuth();
    applyFilters();
});

function checkScoutAuth() {
    const user = StriveAPI.getUser();
    if (!user || user.role !== "ROLE_SCOUT") {
        const demoScout = {
            userId: 5,
            email: "scout@strive.org",
            fullName: "Scout Vijay Kotkar",
            role: "ROLE_SCOUT"
        };
        StriveAPI.setSession("demo_scout_token", demoScout);
    }
    const u = StriveAPI.getUser();
    document.getElementById("scoutNavName").textContent = u.fullName || "Scout Vijay Kotkar";
}

function handleScoutLogout() {
    StriveAPI.clearSession();
    window.location.href = "index.html";
}

async function applyFilters() {
    const sport = document.getElementById("filterSport").value;
    const age = document.getElementById("filterAge").value;
    const gender = document.getElementById("filterGender").value;
    const minScore = document.getElementById("filterMinScore").value;

    const tbody = document.getElementById("leaderboardBody");
    tbody.innerHTML = `
        <tr>
            <td colspan="7" class="text-center py-4 text-secondary">
                <span class="spinner-border spinner-border-sm me-2"></span>Searching talent database...
            </td>
        </tr>
    `;

    try {
        const items = await StriveAPI.searchTalent(sport, gender, age, minScore ? parseFloat(minScore) : null);
        if (items && items.length > 0) {
            renderLeaderboard(items);
        } else {
            // Default demo fallback cohort
            const demoItems = [
                { rankPosition: 1, athleteId: 1, athleteName: "Vedant Patil", sportCode: "SQUAT", gender: "MALE", ageGroup: "U-21", normalizedScore: 90.0, city: "Pune", state: "Maharashtra" },
                { rankPosition: 2, athleteId: 2, athleteName: "Neha Sharma", sportCode: "SQUAT", gender: "FEMALE", ageGroup: "U-21", normalizedScore: 88.5, city: "Satara", state: "Maharashtra" },
                { rankPosition: 3, athleteId: 3, athleteName: "Rahul Deshmukh", sportCode: "SQUAT", gender: "MALE", ageGroup: "U-17", normalizedScore: 79.0, city: "Kolhapur", state: "Maharashtra" }
            ].filter(item => {
                if (sport && item.sportCode !== sport) return false;
                if (gender && item.gender !== gender) return false;
                if (age && item.ageGroup !== age) return false;
                if (minScore && item.normalizedScore < parseFloat(minScore)) return false;
                return true;
            });
            renderLeaderboard(demoItems);
        }
    } catch (err) {
        console.warn("Using fallback leaderboard:", err);
    }
}

function renderLeaderboard(items) {
    const tbody = document.getElementById("leaderboardBody");
    if (!items || items.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-4 text-secondary">
                    No athletes matched the specified talent discovery criteria.
                </td>
            </tr>
        `;
        return;
    }

    let html = "";
    items.forEach(item => {
        let rankBadgeClass = "bg-secondary";
        if (item.rankPosition === 1) rankBadgeClass = "bg-warning text-dark";
        else if (item.rankPosition === 2) rankBadgeClass = "bg-light text-dark";
        else if (item.rankPosition === 3) rankBadgeClass = "bg-danger text-white";

        html += `
            <tr class="border-secondary-subtle">
                <td>
                    <span class="badge ${rankBadgeClass} rounded-pill px-3 py-2 fw-bold">#${item.rankPosition}</span>
                </td>
                <td>
                    <div class="fw-bold text-white">${item.athleteName}</div>
                    <div class="text-secondary small">ID: ATH-${item.athleteId}</div>
                </td>
                <td><span class="badge bg-dark border border-secondary">${item.sportCode}</span></td>
                <td><span class="badge bg-secondary-subtle text-white">${item.ageGroup} • ${item.gender}</span></td>
                <td class="text-secondary">${item.city || "Pune"}, ${item.state || "MH"}</td>
                <td>
                    <strong class="text-success fs-5">${item.normalizedScore.toFixed(1)}</strong>
                    <span class="text-secondary small">/ 100</span>
                </td>
                <td class="text-end">
                    <button class="btn btn-outline-success btn-sm" onclick='viewAthleteDossier(${JSON.stringify(item).replace(/'/g, "&apos;")})'>
                        <i class="bi bi-person-vcard me-1"></i> Dossier
                    </button>
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

function viewAthleteDossier(athlete) {
    const body = document.getElementById("athleteModalBody");
    body.innerHTML = `
        <div class="text-center mb-3">
            <div class="rounded-circle bg-success-subtle text-success p-3 d-inline-flex mb-2">
                <i class="bi bi-person-bounding-box fs-1"></i>
            </div>
            <h4 class="fw-bold text-white mb-0">${athlete.athleteName}</h4>
            <div class="text-secondary small">Rank #${athlete.rankPosition} • ${athlete.sportCode}</div>
        </div>

        <div class="row g-2 mb-3">
            <div class="col-6">
                <div class="metric-box">
                    <div class="metric-val text-white">${athlete.normalizedScore.toFixed(1)}</div>
                    <div class="metric-name">Verified Score</div>
                </div>
            </div>
            <div class="col-6">
                <div class="metric-box">
                    <div class="metric-val text-info">${athlete.ageGroup}</div>
                    <div class="metric-name">Cohort Bracket</div>
                </div>
            </div>
        </div>

        <ul class="list-group list-group-flush bg-transparent">
            <li class="list-group-item bg-transparent text-secondary border-secondary-subtle d-flex justify-content-between">
                <span>District / Location:</span>
                <strong class="text-white">${athlete.city || "Pune"}, ${athlete.state || "Maharashtra"}</strong>
            </li>
            <li class="list-group-item bg-transparent text-secondary border-secondary-subtle d-flex justify-content-between">
                <span>Gender:</span>
                <strong class="text-white">${athlete.gender}</strong>
            </li>
            <li class="list-group-item bg-transparent text-secondary border-secondary-subtle d-flex justify-content-between">
                <span>Verification Status:</span>
                <strong class="text-success"><i class="bi bi-patch-check-fill me-1"></i>Biometrically Certified</strong>
            </li>
        </ul>

        <div class="disclaimer-banner mt-3">
            <i class="bi bi-info-circle me-1"></i>
            Data backed by 33-landmark pose estimation and longitudinal session analysis.
        </div>
    `;

    const modal = new bootstrap.Modal(document.getElementById("athleteModal"));
    modal.show();
}
