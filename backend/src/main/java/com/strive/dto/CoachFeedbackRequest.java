package com.strive.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public class CoachFeedbackRequest {
    @NotNull(message = "Athlete ID is required")
    private Long athleteId;

    @NotBlank(message = "Feedback notes cannot be blank")
    private String feedbackNotes;

    public CoachFeedbackRequest() {}

    public Long getAthleteId() { return athleteId; }
    public void setAthleteId(Long athleteId) { this.athleteId = athleteId; }

    public String getFeedbackNotes() { return feedbackNotes; }
    public void setFeedbackNotes(String feedbackNotes) { this.feedbackNotes = feedbackNotes; }
}
