package com.strive.dto;

import java.time.LocalDateTime;

public class AssessmentResponse {
    private Long id;
    private Long videoId;
    private Long athleteId;
    private String athleteName;
    private String sportCode;
    private String sportName;
    private Double score;
    private Double confidenceScore;
    private Double movementDeviation;
    private Integer repCount;
    private String injuryRiskLevel;
    private String injuryInsights;
    private String annotatedVideoUrl;
    private LocalDateTime assessedAt;

    public AssessmentResponse() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getVideoId() { return videoId; }
    public void setVideoId(Long videoId) { this.videoId = videoId; }

    public Long getAthleteId() { return athleteId; }
    public void setAthleteId(Long athleteId) { this.athleteId = athleteId; }

    public String getAthleteName() { return athleteName; }
    public void setAthleteName(String athleteName) { this.athleteName = athleteName; }

    public String getSportCode() { return sportCode; }
    public void setSportCode(String sportCode) { this.sportCode = sportCode; }

    public String getSportName() { return sportName; }
    public void setSportName(String sportName) { this.sportName = sportName; }

    public Double getScore() { return score; }
    public void setScore(Double score) { this.score = score; }

    public Double getConfidenceScore() { return confidenceScore; }
    public void setConfidenceScore(Double confidenceScore) { this.confidenceScore = confidenceScore; }

    public Double getMovementDeviation() { return movementDeviation; }
    public void setMovementDeviation(Double movementDeviation) { this.movementDeviation = movementDeviation; }

    public Integer getRepCount() { return repCount; }
    public void setRepCount(Integer repCount) { this.repCount = repCount; }

    public String getInjuryRiskLevel() { return injuryRiskLevel; }
    public void setInjuryRiskLevel(String injuryRiskLevel) { this.injuryRiskLevel = injuryRiskLevel; }

    public String getInjuryInsights() { return injuryInsights; }
    public void setInjuryInsights(String injuryInsights) { this.injuryInsights = injuryInsights; }

    public String getAnnotatedVideoUrl() { return annotatedVideoUrl; }
    public void setAnnotatedVideoUrl(String annotatedVideoUrl) { this.annotatedVideoUrl = annotatedVideoUrl; }

    public LocalDateTime getAssessedAt() { return assessedAt; }
    public void setAssessedAt(LocalDateTime assessedAt) { this.assessedAt = assessedAt; }
}
