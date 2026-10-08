package com.strive.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "videos")
public class Video {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "athlete_id", nullable = false)
    private AthleteProfile athlete;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "sports_activity_id", nullable = false)
    private SportsActivity sportsActivity;

    private String originalFilename;
    private String storagePath;
    private String annotatedPath;
    private Double durationSeconds;
    private Double fps;

    @Column(nullable = false)
    private String status = "UPLOADED"; // UPLOADED, ANALYZED, FAILED

    private LocalDateTime uploadedAt = LocalDateTime.now();

    public Video() {}

    public Video(AthleteProfile athlete, SportsActivity sportsActivity, String originalFilename, String storagePath) {
        this.athlete = athlete;
        this.sportsActivity = sportsActivity;
        this.originalFilename = originalFilename;
        this.storagePath = storagePath;
        this.uploadedAt = LocalDateTime.now();
        this.status = "UPLOADED";
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public AthleteProfile getAthlete() { return athlete; }
    public void setAthlete(AthleteProfile athlete) { this.athlete = athlete; }

    public SportsActivity getSportsActivity() { return sportsActivity; }
    public void setSportsActivity(SportsActivity sportsActivity) { this.sportsActivity = sportsActivity; }

    public String getOriginalFilename() { return originalFilename; }
    public void setOriginalFilename(String originalFilename) { this.originalFilename = originalFilename; }

    public String getStoragePath() { return storagePath; }
    public void setStoragePath(String storagePath) { this.storagePath = storagePath; }

    public String getAnnotatedPath() { return annotatedPath; }
    public void setAnnotatedPath(String annotatedPath) { this.annotatedPath = annotatedPath; }

    public Double getDurationSeconds() { return durationSeconds; }
    public void setDurationSeconds(Double durationSeconds) { this.durationSeconds = durationSeconds; }

    public Double getFps() { return fps; }
    public void setFps(Double fps) { this.fps = fps; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public LocalDateTime getUploadedAt() { return uploadedAt; }
    public void setUploadedAt(LocalDateTime uploadedAt) { this.uploadedAt = uploadedAt; }
}
