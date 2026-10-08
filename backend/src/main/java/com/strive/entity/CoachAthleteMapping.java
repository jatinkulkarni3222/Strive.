package com.strive.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "coach_athlete_mappings")
public class CoachAthleteMapping {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "coach_id", nullable = false)
    private User coach;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "athlete_id", nullable = false)
    private AthleteProfile athlete;

    @Column(length = 2000)
    private String feedbackNotes;

    private LocalDateTime assignedAt = LocalDateTime.now();

    public CoachAthleteMapping() {}

    public CoachAthleteMapping(User coach, AthleteProfile athlete, String feedbackNotes) {
        this.coach = coach;
        this.athlete = athlete;
        this.feedbackNotes = feedbackNotes;
        this.assignedAt = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public User getCoach() { return coach; }
    public void setCoach(User coach) { this.coach = coach; }

    public AthleteProfile getAthlete() { return athlete; }
    public void setAthlete(AthleteProfile athlete) { this.athlete = athlete; }

    public String getFeedbackNotes() { return feedbackNotes; }
    public void setFeedbackNotes(String feedbackNotes) { this.feedbackNotes = feedbackNotes; }

    public LocalDateTime getAssignedAt() { return assignedAt; }
    public void setAssignedAt(LocalDateTime assignedAt) { this.assignedAt = assignedAt; }
}
