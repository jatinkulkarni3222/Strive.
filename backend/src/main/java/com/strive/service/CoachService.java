package com.strive.service;

import com.strive.dto.CoachFeedbackRequest;
import com.strive.entity.AthleteProfile;
import com.strive.entity.CoachAthleteMapping;
import com.strive.entity.User;
import com.strive.exception.ResourceNotFoundException;
import com.strive.repository.AthleteProfileRepository;
import com.strive.repository.CoachAthleteMappingRepository;
import com.strive.repository.UserRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class CoachService {

    private final CoachAthleteMappingRepository mappingRepository;
    private final UserRepository userRepository;
    private final AthleteProfileRepository athleteProfileRepository;

    public CoachService(CoachAthleteMappingRepository mappingRepository,
                        UserRepository userRepository,
                        AthleteProfileRepository athleteProfileRepository) {
        this.mappingRepository = mappingRepository;
        this.userRepository = userRepository;
        this.athleteProfileRepository = athleteProfileRepository;
    }

    public List<CoachAthleteMapping> getAssignedAthletes(String coachEmail) {
        User coach = userRepository.findByEmail(coachEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Coach not found with email: " + coachEmail));
        return mappingRepository.findByCoach(coach);
    }

    @Transactional
    public CoachAthleteMapping provideFeedback(String coachEmail, CoachFeedbackRequest request) {
        User coach = userRepository.findByEmail(coachEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Coach not found with email: " + coachEmail));

        AthleteProfile athlete = athleteProfileRepository.findById(request.getAthleteId())
                .orElseThrow(() -> new ResourceNotFoundException("Athlete not found with ID: " + request.getAthleteId()));

        CoachAthleteMapping mapping = mappingRepository.findByCoachAndAthleteId(coach, athlete.getId())
                .orElse(new CoachAthleteMapping(coach, athlete, ""));

        mapping.setFeedbackNotes(request.getFeedbackNotes());
        mapping.setAssignedAt(LocalDateTime.now());
        return mappingRepository.save(mapping);
    }
}
