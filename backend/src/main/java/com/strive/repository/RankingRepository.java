package com.strive.repository;

import com.strive.entity.Ranking;
import com.strive.entity.SportsActivity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface RankingRepository extends JpaRepository<Ranking, Long> {
    List<Ranking> findBySportsActivityOrderByRankPositionAsc(SportsActivity sportsActivity);

    @Query("SELECT r FROM Ranking r WHERE " +
           "(:sportsActivity IS NULL OR r.sportsActivity = :sportsActivity) AND " +
           "(:gender IS NULL OR r.gender = :gender) AND " +
           "(:ageGroup IS NULL OR r.ageGroup = :ageGroup) " +
           "ORDER BY r.normalizedScore DESC")
    List<Ranking> filterRankings(
            @Param("sportsActivity") SportsActivity sportsActivity,
            @Param("gender") String gender,
            @Param("ageGroup") String ageGroup
    );

    Optional<Ranking> findByAthleteIdAndSportsActivity(Long athleteId, SportsActivity sportsActivity);
}
