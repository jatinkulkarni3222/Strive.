package com.strive.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "progress_records")
public class ProgressRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "athlete_id", nullable = false)
    private AthleteProfile athlete;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "sports_activity_id", nullable = false)
    private SportsActivity sportsActivity;

    private Integer sessionNumber;
    private Double currentScore;
    private Double previousScore;
    private Double improvementPercentage; // Equation 1.9.9: ((St - St-1) / St-1) * 100
    private LocalDateTime recordedAt = LocalDateTime.now();

    public ProgressRecord() {}

    public ProgressRecord(AthleteProfile athlete, SportsActivity sportsActivity, Integer sessionNumber,
                          Double currentScore, Double previousScore, Double improvementPercentage) {
        this.athlete = athlete;
        this.sportsActivity = sportsActivity;
        this.sessionNumber = sessionNumber;
        this.currentScore = currentScore;
        this.previousScore = previousScore;
        this.improvementPercentage = improvementPercentage;
        this.recordedAt = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public AthleteProfile getAthlete() { return athlete; }
    public void setAthlete(AthleteProfile athlete) { this.athlete = athlete; }

    public SportsActivity getSportsActivity() { return sportsActivity; }
    public void setSportsActivity(SportsActivity sportsActivity) { this.sportsActivity = sportsActivity; }

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
