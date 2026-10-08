package com.strive.repository;

import com.strive.entity.CoachAthleteMapping;
import com.strive.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CoachAthleteMappingRepository extends JpaRepository<CoachAthleteMapping, Long> {
    List<CoachAthleteMapping> findByCoach(User coach);
    List<CoachAthleteMapping> findByCoachId(Long coachId);
    Optional<CoachAthleteMapping> findByCoachAndAthleteId(User coach, Long athleteId);
}
