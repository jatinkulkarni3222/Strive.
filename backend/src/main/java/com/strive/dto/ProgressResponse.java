package com.strive.dto;

import java.time.LocalDateTime;

public class ProgressResponse {
    private Integer sessionNumber;
    private Double currentScore;
    private Double previousScore;
    private Double improvementPercentage;
    private LocalDateTime recordedAt;

    public ProgressResponse() {}

    public ProgressResponse(Integer sessionNumber, Double currentScore, Double previousScore, Double improvementPercentage, LocalDateTime recordedAt) {
        this.sessionNumber = sessionNumber;
        this.currentScore = currentScore;
        this.previousScore = previousScore;
        this.improvementPercentage = improvementPercentage;
        this.recordedAt = recordedAt;
    }

    public Integer getSessionNumber() { return sessionNumber; }
    public void setSessionNumber(Integer sessionNumber) { this.sessionNumber = sessionNumber; }

    public Double getCurrentScore() { return currentScore; }
    public void setCurrentScore(Double currentScore) { this.currentScore = currentScore; }

    public Double getPreviousScore() { return previousScore; }
    public void setPreviousScore(Double previousScore) { this.previousScore = previousScore; }

    public Double getImprovementPercentage() { return improvementPercentage; }
    public void setImprovementPercentage(Double improvementPercentage) { this.improvementPercentage = improvementPercentage; }

    public LocalDateTime getRecordedAt() { return recordedAt; }
    public void setRecordedAt(LocalDateTime recordedAt) { this.recordedAt = recordedAt; }
}
