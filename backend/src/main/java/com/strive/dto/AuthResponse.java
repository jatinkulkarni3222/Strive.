package com.strive.dto;

import com.strive.entity.Role;

public class AuthResponse {
    private String token;
    private Long userId;
    private String email;
    private String fullName;
    private Role role;
    private Long athleteProfileId;

    public AuthResponse() {}

    public AuthResponse(String token, Long userId, String email, String fullName, Role role, Long athleteProfileId) {
        this.token = token;
        this.userId = userId;
        this.email = email;
        this.fullName = fullName;
        this.role = role;
        this.athleteProfileId = athleteProfileId;
    }

    public String getToken() { return token; }
    public void setToken(String token) { this.token = token; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getFullName() { return fullName; }
    public void setFullName(String fullName) { this.fullName = fullName; }

    public Role getRole() { return role; }
    public void setRole(Role role) { this.role = role; }

    public Long getAthleteProfileId() { return athleteProfileId; }
    public void setAthleteProfileId(Long athleteProfileId) { this.athleteProfileId = athleteProfileId; }
}
