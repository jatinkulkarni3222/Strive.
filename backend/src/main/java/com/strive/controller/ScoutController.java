package com.strive.controller;

import com.strive.dto.LeaderboardItemResponse;
import com.strive.entity.AthleteProfile;
import com.strive.service.ScoutService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/scout")
@Tag(name = "Scout Module", description = "Talent discovery, athlete search, and multi-criteria screening")
public class ScoutController {

    private final ScoutService scoutService;

    public ScoutController(ScoutService scoutService) {
        this.scoutService = scoutService;
    }

    @GetMapping("/athletes")
    @Operation(summary = "Search and filter emerging athletes by sport, age group, gender, and score")
    public ResponseEntity<List<LeaderboardItemResponse>> searchTalent(
            @RequestParam(value = "sport", required = false) String sportCode,
            @RequestParam(value = "gender", required = false) String gender,
            @RequestParam(value = "ageGroup", required = false) String ageGroup,
            @RequestParam(value = "minScore", required = false) Double minScore) {
        return ResponseEntity.ok(scoutService.searchTalent(sportCode, gender, ageGroup, minScore));
    }

    @GetMapping("/athletes/{athleteId}")
    @Operation(summary = "View comprehensive athlete profile and biodata")
    public ResponseEntity<AthleteProfile> getAthleteDetails(@PathVariable("athleteId") Long athleteId) {
        return ResponseEntity.ok(scoutService.getAthleteDetails(athleteId));
    }
}
