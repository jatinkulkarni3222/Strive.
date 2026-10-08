package com.strive.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "rankings")
public class Ranking {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "athlete_id", nullable = false)
    private AthleteProfile athlete;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "sports_activity_id", nullable = false)
    private SportsActivity sportsActivity;

    private Double normalizedScore;
    private Integer rankPosition;
    private String ageGroup; // U-17, U-21, SENIOR
    private String gender;   // MALE, FEMALE
    private LocalDateTime updatedAt = LocalDateTime.now();

    public Ranking() {}

    public Ranking(AthleteProfile athlete, SportsActivity sportsActivity, Double normalizedScore,
                   Integer rankPosition, String ageGroup, String gender) {
        this.athlete = athlete;
        this.sportsActivity = sportsActivity;
        this.normalizedScore = normalizedScore;
        this.rankPosition = rankPosition;
        this.ageGroup = ageGroup;
        this.gender = gender;
        this.updatedAt = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public AthleteProfile getAthlete() { return athlete; }
    public void setAthlete(AthleteProfile athlete) { this.athlete = athlete; }

    public SportsActivity getSportsActivity() { return sportsActivity; }
    public void setSportsActivity(SportsActivity sportsActivity) { this.sportsActivity = sportsActivity; }

    public Double getNormalizedScore() { return normalizedScore; }
    public void setNormalizedScore(Double normalizedScore) { this.normalizedScore = normalizedScore; }

    public Integer getRankPosition() { return rankPosition; }
    public void setRankPosition(Integer rankPosition) { this.rankPosition = rankPosition; }

    public String getAgeGroup() { return ageGroup; }
    public void setAgeGroup(String ageGroup) { this.ageGroup = ageGroup; }

    public String getGender() { return gender; }
    public void setGender(String gender) { this.gender = gender; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
}
