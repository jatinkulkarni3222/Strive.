package com.strive.controller;

import com.strive.dto.ProgressResponse;
import com.strive.entity.AthleteProfile;
import com.strive.entity.SportsActivity;
import com.strive.exception.ResourceNotFoundException;
import com.strive.repository.AthleteProfileRepository;
import com.strive.repository.SportsActivityRepository;
import com.strive.service.ProgressService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/athlete")
@Tag(name = "Athlete Operations", description = "Athlete profile, longitudinal tracking, and performance history")
public class AthleteController {

    private final AthleteProfileRepository athleteProfileRepository;
    private final SportsActivityRepository sportsActivityRepository;
    private final ProgressService progressService;

    public AthleteController(AthleteProfileRepository athleteProfileRepository,
                             SportsActivityRepository sportsActivityRepository,
                             ProgressService progressService) {
        this.athleteProfileRepository = athleteProfileRepository;
        this.sportsActivityRepository = sportsActivityRepository;
        this.progressService = progressService;
    }

    @GetMapping("/profile")
    @Operation(summary = "Get current authenticated athlete profile")
    public ResponseEntity<AthleteProfile> getCurrentProfile(Authentication authentication) {
        String email = authentication.getName();
        AthleteProfile profile = athleteProfileRepository.findAll().stream()
                .filter(p -> p.getUser().getEmail().equalsIgnoreCase(email))
                .findFirst()
                .orElseThrow(() -> new ResourceNotFoundException("Athlete profile not found for user: " + email));
        return ResponseEntity.ok(profile);
    }

    @GetMapping("/{athleteId}/progress")
    @Operation(summary = "Get longitudinal progress with improvement percentage (Equation 1.9.9)")
    public ResponseEntity<List<ProgressResponse>> getProgress(
            @PathVariable("athleteId") Long athleteId,
            @RequestParam(value = "sport", required = false) String sportCode) {
        AthleteProfile athlete = athleteProfileRepository.findById(athleteId)
                .orElseThrow(() -> new ResourceNotFoundException("Athlete profile not found with ID: " + athleteId));

        SportsActivity activity = null;
        if (sportCode != null && !sportCode.isBlank()) {
            activity = sportsActivityRepository.findByCode(sportCode.toUpperCase()).orElse(null);
        }

        return ResponseEntity.ok(progressService.getAthleteProgressHistory(athlete, activity));
    }
}
