package com.strive.dto;

public class LeaderboardItemResponse {
    private Integer rankPosition;
    private Long athleteId;
    private String athleteName;
    private String gender;
    private String ageGroup;
    private String sportCode;
    private Double normalizedScore;
    private String city;
    private String state;

    public LeaderboardItemResponse() {}

    public LeaderboardItemResponse(Integer rankPosition, Long athleteId, String athleteName, String gender,
                                   String ageGroup, String sportCode, Double normalizedScore, String city, String state) {
        this.rankPosition = rankPosition;
        this.athleteId = athleteId;
        this.athleteName = athleteName;
        this.gender = gender;
        this.ageGroup = ageGroup;
        this.sportCode = sportCode;
        this.normalizedScore = normalizedScore;
        this.city = city;
        this.state = state;
    }

    public Integer getRankPosition() { return rankPosition; }
    public void setRankPosition(Integer rankPosition) { this.rankPosition = rankPosition; }

    public Long getAthleteId() { return athleteId; }
    public void setAthleteId(Long athleteId) { this.athleteId = athleteId; }

    public String getAthleteName() { return athleteName; }
    public void setAthleteName(String athleteName) { this.athleteName = athleteName; }

    public String getGender() { return gender; }
    public void setGender(String gender) { this.gender = gender; }

    public String getAgeGroup() { return ageGroup; }
    public void setAgeGroup(String ageGroup) { this.ageGroup = ageGroup; }

    public String getSportCode() { return sportCode; }
    public void setSportCode(String sportCode) { this.sportCode = sportCode; }

    public Double getNormalizedScore() { return normalizedScore; }
    public void setNormalizedScore(Double normalizedScore) { this.normalizedScore = normalizedScore; }

    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }

    public String getState() { return state; }
    public void setState(String state) { this.state = state; }
}
