/**
 * STRIVE API Client Module
 * Manages JWT sessions, REST communication with Spring Boot backend & CV service.
 */
const API_BASE_URL = window.STRIVE_API_BASE || "http://localhost:8080/api";
const CV_BASE_URL = window.STRIVE_CV_BASE || "http://localhost:8000";

const StriveAPI = {
    // Auth Session
    getToken() {
        return localStorage.getItem("strive_token");
    },
    getUser() {
        const u = localStorage.getItem("strive_user");
        return u ? JSON.parse(u) : null;
    },
    setSession(token, user) {
        localStorage.setItem("strive_token", token);
        localStorage.setItem("strive_user", JSON.stringify(user));
    },
    clearSession() {
        localStorage.removeItem("strive_token");
        localStorage.removeItem("strive_user");
    },
    isAuthenticated() {
        return !!this.getToken();
    },

    // HTTP Request Helper
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = options.headers || {};

        const token = this.getToken();
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
            headers["Content-Type"] = "application/json";
        }

        const config = {
            ...options,
            headers
        };

        try {
            const res = await fetch(url, config);
            if (res.status === 401) {
                this.clearSession();
                window.location.href = "index.html";
                return null;
            }
            if (!res.ok) {
                const errData = await res.json().catch(() => ({ message: res.statusText }));
                throw new Error(errData.message || `Request failed with status ${res.status}`);
            }
            return await res.json();
        } catch (err) {
            console.error("API Error:", err);
            throw err;
        }
    },

    // Auth Endpoints
    async login(email, password) {
        const data = await this.request("/auth/login", {
            method: "POST",
            body: JSON.stringify({ email, password })
        });
        if (data && data.token) {
            this.setSession(data.token, data);
        }
        return data;
    },

    async register(regData) {
        const data = await this.request("/auth/register", {
            method: "POST",
            body: JSON.stringify(regData)
        });
        if (data && data.token) {
            this.setSession(data.token, data);
        }
        return data;
    },

    // Video Assessment
    async uploadVideo(athleteId, sport, file) {
        const formData = new FormData();
        formData.append("athleteId", athleteId);
        formData.append("sport", sport);
        formData.append("video", file);

        return await this.request("/assessments/upload", {
            method: "POST",
            body: formData
        });
    },

    async getAssessment(id) {
        return await this.request(`/assessments/${id}`);
    },

    async getAthleteAssessments(athleteId) {
        return await this.request(`/assessments/athlete/${athleteId}`);
    },

    // Longitudinal Progress
    async getProgress(athleteId, sport = "") {
        const q = sport ? `?sport=${encodeURIComponent(sport)}` : "";
        return await this.request(`/athlete/${athleteId}/progress${q}`);
    },

    // Rankings / Leaderboard
    async getRankings(sport = "", gender = "", ageGroup = "") {
        const params = new URLSearchParams();
        if (sport) params.append("sport", sport);
        if (gender) params.append("gender", gender);
        if (ageGroup) params.append("ageGroup", ageGroup);
        const q = params.toString() ? `?${params.toString()}` : "";
        return await this.request(`/rankings${q}`);
    },

    // Coach Operations
    async getCoachAthletes() {
        return await this.request("/coach/athletes");
    },

    async submitCoachFeedback(athleteId, feedbackNotes) {
        return await this.request("/coach/feedback", {
            method: "POST",
            body: JSON.stringify({ athleteId, feedbackNotes })
        });
    },

    // Scout Operations
    async searchTalent(sport = "", gender = "", ageGroup = "", minScore = null) {
        const params = new URLSearchParams();
        if (sport) params.append("sport", sport);
        if (gender) params.append("gender", gender);
        if (ageGroup) params.append("ageGroup", ageGroup);
        if (minScore != null) params.append("minScore", minScore);
        const q = params.toString() ? `?${params.toString()}` : "";
        return await this.request(`/scout/athletes${q}`);
    },

    async getScoutAthleteDetails(athleteId) {
        return await this.request(`/scout/athletes/${athleteId}`);
    },

    // Media streaming URL resolver
    resolveAnnotatedUrl(urlOrPath) {
        if (!urlOrPath) return "";
        if (urlOrPath.startsWith("http")) return urlOrPath;
        return `${CV_BASE_URL}${urlOrPath}`;
    }
};

window.StriveAPI = StriveAPI;
