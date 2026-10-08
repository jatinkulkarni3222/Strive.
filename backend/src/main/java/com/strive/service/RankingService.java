package com.strive.service;

import com.strive.dto.LeaderboardItemResponse;
import com.strive.entity.AthleteProfile;
import com.strive.entity.Ranking;
import com.strive.entity.SportsActivity;
import com.strive.repository.RankingRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class RankingService {

    private final RankingRepository rankingRepository;

    public RankingService(RankingRepository rankingRepository) {
        this.rankingRepository = rankingRepository;
    }

    /**
     * Update athlete's ranking and recalculate positions across cohort.
     * Equation (1.9.10): R_i = rank(S_i)
     */
    @Transactional
    public void updateAthleteRanking(AthleteProfile athlete, SportsActivity activity, Double score) {
        Optional<Ranking> existingOpt = rankingRepository.findByAthleteIdAndSportsActivity(athlete.getId(), activity);

        Ranking ranking;
        if (existingOpt.isPresent()) {
            ranking = existingOpt.get();
            // Retain personal best score or update
            if (score > ranking.getNormalizedScore()) {
                ranking.setNormalizedScore(score);
                ranking.setUpdatedAt(LocalDateTime.now());
            }
        } else {
            ranking = new Ranking(
                    athlete,
                    activity,
                    score,
                    999, // default rank before sorting
                    athlete.getAgeGroup(),
                    athlete.getGender() != null ? athlete.getGender().toUpperCase() : "MALE"
            );
        }
        rankingRepository.save(ranking);

        // Recalculate rank positions for this sport
        List<Ranking> allRankings = rankingRepository.findBySportsActivityOrderByRankPositionAsc(activity);
        allRankings.sort((a, b) -> Double.compare(b.getNormalizedScore(), a.getNormalizedScore()));

        for (int i = 0; i < allRankings.size(); i++) {
            allRankings.get(i).setRankPosition(i + 1);
        }
        rankingRepository.saveAll(allRankings);
    }

    public List<LeaderboardItemResponse> getLeaderboard(SportsActivity activity, String gender, String ageGroup) {
        List<Ranking> rankings = rankingRepository.filterRankings(activity, gender, ageGroup);
        return rankings.stream()
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
}
