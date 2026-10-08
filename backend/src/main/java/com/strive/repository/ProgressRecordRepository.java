package com.strive.repository;

import com.strive.entity.AthleteProfile;
import com.strive.entity.ProgressRecord;
import com.strive.entity.SportsActivity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ProgressRecordRepository extends JpaRepository<ProgressRecord, Long> {
    List<ProgressRecord> findByAthleteOrderByRecordedAtAsc(AthleteProfile athlete);
    List<ProgressRecord> findByAthleteAndSportsActivityOrderBySessionNumberAsc(AthleteProfile athlete, SportsActivity sportsActivity);
    Optional<ProgressRecord> findTopByAthleteAndSportsActivityOrderBySessionNumberDesc(AthleteProfile athlete, SportsActivity sportsActivity);
}
