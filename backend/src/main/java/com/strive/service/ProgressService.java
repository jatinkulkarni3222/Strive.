package com.strive.service;

import com.strive.dto.ProgressResponse;
import com.strive.entity.AthleteProfile;
import com.strive.entity.ProgressRecord;
import com.strive.entity.SportsActivity;
import com.strive.repository.ProgressRecordRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class ProgressService {

    private final ProgressRecordRepository progressRecordRepository;

    public ProgressService(ProgressRecordRepository progressRecordRepository) {
        this.progressRecordRepository = progressRecordRepository;
    }

    /**
     * Compute longitudinal improvement percentage and record progress session.
     * Equation (1.9.9):
     *     I = ((St - St-1) / St-1) * 100
     */
    @Transactional
    public ProgressRecord recordAssessmentProgress(AthleteProfile athlete, SportsActivity activity, Double newScore) {
        Optional<ProgressRecord> latestOpt = progressRecordRepository
                .findTopByAthleteAndSportsActivityOrderBySessionNumberDesc(athlete, activity);

        int sessionNumber = 1;
        double previousScore = newScore;
        double improvementPercentage = 0.0;

        if (latestOpt.isPresent()) {
            ProgressRecord previous = latestOpt.get();
            sessionNumber = previous.getSessionNumber() + 1;
            previousScore = previous.getCurrentScore();
            if (previousScore > 0.0) {
                // Equation (1.9.9)
                improvementPercentage = ((newScore - previousScore) / previousScore) * 100.0;
            }
        }

        ProgressRecord progressRecord = new ProgressRecord(
                athlete,
                activity,
                sessionNumber,
                newScore,
                previousScore,
                Math.round(improvementPercentage * 100.0) / 100.0
        );

        return progressRecordRepository.save(progressRecord);
    }

    public List<ProgressResponse> getAthleteProgressHistory(AthleteProfile athlete, SportsActivity activity) {
        List<ProgressRecord> records = (activity == null)
                ? progressRecordRepository.findByAthleteOrderByRecordedAtAsc(athlete)
                : progressRecordRepository.findByAthleteAndSportsActivityOrderBySessionNumberAsc(athlete, activity);

        return records.stream()
                .map(r -> new ProgressResponse(
                        r.getSessionNumber(),
                        r.getCurrentScore(),
                        r.getPreviousScore(),
                        r.getImprovementPercentage(),
                        r.getRecordedAt()
                ))
                .collect(Collectors.toList());
    }
}
