package com.strive.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "assessments")
public class Assessment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "video_id", nullable = false, unique = true)
    private Video video;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "athlete_id", nullable = false)
    private AthleteProfile athlete;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "sports_activity_id", nullable = false)
    private SportsActivity sportsActivity;

    private Double score;
    private Double confidenceScore;
    private Double movementDeviation;
    private Integer repCount;
    private String injuryRiskLevel; // LOW, MEDIUM, HIGH

    @Column(length = 4000)
    private String injuryInsights;

    private LocalDateTime assessedAt = LocalDateTime.now();

    public Assessment() {}

    public Assessment(Video video, AthleteProfile athlete, SportsActivity sportsActivity, Double score,
                      Double confidenceScore, Double movementDeviation, Integer repCount,
                      String injuryRiskLevel, String injuryInsights) {
        this.video = video;
        this.athlete = athlete;
        this.sportsActivity = sportsActivity;
        this.score = score;
        this.confidenceScore = confidenceScore;
        this.movementDeviation = movementDeviation;
        this.repCount = repCount;
        this.injuryRiskLevel = injuryRiskLevel;
        this.injuryInsights = injuryInsights;
        this.assessedAt = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Video getVideo() { return video; }
    public void setVideo(Video video) { this.video = video; }

    public AthleteProfile getAthlete() { return athlete; }
    public void setAthlete(AthleteProfile athlete) { this.athlete = athlete; }

    public SportsActivity getSportsActivity() { return sportsActivity; }
    public void setSportsActivity(SportsActivity sportsActivity) { this.sportsActivity = sportsActivity; }

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

    public LocalDateTime getAssessedAt() { return assessedAt; }
    public void setAssessedAt(LocalDateTime assessedAt) { this.assessedAt = assessedAt; }
}
