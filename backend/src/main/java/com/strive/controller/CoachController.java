package com.strive.controller;

import com.strive.dto.CoachFeedbackRequest;
import com.strive.entity.CoachAthleteMapping;
import com.strive.service.CoachService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/coach")
@Tag(name = "Coach Module", description = "Coach athlete monitoring, progress review, and feedback")
public class CoachController {

    private final CoachService coachService;

    public CoachController(CoachService coachService) {
        this.coachService = coachService;
    }

    @GetMapping("/athletes")
    @Operation(summary = "View athletes assigned to the coach")
    public ResponseEntity<List<CoachAthleteMapping>> getAssignedAthletes(Authentication authentication) {
        return ResponseEntity.ok(coachService.getAssignedAthletes(authentication.getName()));
    }

    @PostMapping("/feedback")
    @Operation(summary = "Submit coaching observations and corrective feedback")
    public ResponseEntity<CoachAthleteMapping> submitFeedback(
            Authentication authentication,
            @Valid @RequestBody CoachFeedbackRequest request) {
        return ResponseEntity.ok(coachService.provideFeedback(authentication.getName(), request));
    }
}
