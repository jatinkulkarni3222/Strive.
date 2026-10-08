package com.strive.controller;

import com.strive.dto.LeaderboardItemResponse;
import com.strive.entity.SportsActivity;
import com.strive.repository.SportsActivityRepository;
import com.strive.service.RankingService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/rankings")
@Tag(name = "Rankings & Leaderboards", description = "Performance rankings sorted by normalized score (Equation 1.9.10)")
public class RankingController {

    private final RankingService rankingService;
    private final SportsActivityRepository sportsActivityRepository;

    public RankingController(RankingService rankingService, SportsActivityRepository sportsActivityRepository) {
        this.rankingService = rankingService;
        this.sportsActivityRepository = sportsActivityRepository;
    }

    @GetMapping
    @Operation(summary = "Get cohort leaderboard filtered by sport, gender, and age group")
    public ResponseEntity<List<LeaderboardItemResponse>> getLeaderboard(
            @RequestParam(value = "sport", required = false) String sportCode,
            @RequestParam(value = "gender", required = false) String gender,
            @RequestParam(value = "ageGroup", required = false) String ageGroup) {

        SportsActivity activity = null;
        if (sportCode != null && !sportCode.isBlank()) {
            activity = sportsActivityRepository.findByCode(sportCode.toUpperCase()).orElse(null);
        }

        List<LeaderboardItemResponse> leaderboard = rankingService.getLeaderboard(activity, gender, ageGroup);
        return ResponseEntity.ok(leaderboard);
    }
}
