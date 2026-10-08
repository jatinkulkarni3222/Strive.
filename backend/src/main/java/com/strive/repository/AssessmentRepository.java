package com.strive.repository;

import com.strive.entity.Assessment;
import com.strive.entity.AthleteProfile;
import com.strive.entity.SportsActivity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AssessmentRepository extends JpaRepository<Assessment, Long> {
    List<Assessment> findByAthleteOrderByAssessedAtDesc(AthleteProfile athlete);
    List<Assessment> findByAthleteAndSportsActivityOrderByAssessedAtAsc(AthleteProfile athlete, SportsActivity sportsActivity);
    Optional<Assessment> findByVideoId(Long videoId);
    List<Assessment> findBySportsActivityOrderByScoreDesc(SportsActivity sportsActivity);
}
