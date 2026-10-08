package com.strive.service;

import com.strive.dto.LeaderboardItemResponse;
import com.strive.entity.AthleteProfile;
import com.strive.entity.Ranking;
import com.strive.entity.SportsActivity;
import com.strive.exception.ResourceNotFoundException;
import com.strive.repository.AthleteProfileRepository;
import com.strive.repository.RankingRepository;
import com.strive.repository.SportsActivityRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class ScoutService {

    private final RankingRepository rankingRepository;
    private final AthleteProfileRepository athleteProfileRepository;
    private final SportsActivityRepository sportsActivityRepository;

    public ScoutService(RankingRepository rankingRepository,
                        AthleteProfileRepository athleteProfileRepository,
                        SportsActivityRepository sportsActivityRepository) {
        this.rankingRepository = rankingRepository;
        this.athleteProfileRepository = athleteProfileRepository;
        this.sportsActivityRepository = sportsActivityRepository;
    }

    public List<LeaderboardItemResponse> searchTalent(String sportCode, String gender, String ageGroup, Double minScore) {
        SportsActivity activity = null;
        if (sportCode != null && !sportCode.isBlank()) {
            activity = sportsActivityRepository.findByCode(sportCode.toUpperCase()).orElse(null);
        }

        List<Ranking> rankings = rankingRepository.filterRankings(activity, gender, ageGroup);

        return rankings.stream()
                .filter(r -> minScore == null || r.getNormalizedScore() >= minScore)
                .map(r -> new LeaderboardItemResponse(
                        r.getRankPosition(),
                        r.getAthlete().getId(),
                        r.getAthlete().getUser().getFullName(),
                        r.getGender(),
                        r.getAgeGroup(),
                        r.getSportsActivity().getCode(),
                        r.getNormalizedScore(),
                        r.getAthlete().getCity(),
                        r.getAthlete().getState()
                ))
                .collect(Collectors.toList());
    }

    public AthleteProfile getAthleteDetails(Long athleteId) {
        return athleteProfileRepository.findById(athleteId)
                .orElseThrow(() -> new ResourceNotFoundException("Athlete profile not found with ID: " + athleteId));
    }
}
