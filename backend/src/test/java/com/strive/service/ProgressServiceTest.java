package com.strive.service;

import com.strive.entity.AthleteProfile;
import com.strive.entity.ProgressRecord;
import com.strive.entity.SportsActivity;
import com.strive.repository.ProgressRecordRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class ProgressServiceTest {

    @Mock
    private ProgressRecordRepository progressRecordRepository;

    private ProgressService progressService;

    @BeforeEach
    void setUp() {
        progressService = new ProgressService(progressRecordRepository);
    }

    @Test
    void testFirstSessionZeroImprovement() {
        AthleteProfile athlete = new AthleteProfile();
        athlete.setId(1L);
        SportsActivity squat = new SportsActivity("SQUAT", "Squat", "Squat Activity");

        when(progressRecordRepository.findTopByAthleteAndSportsActivityOrderBySessionNumberDesc(athlete, squat))
                .thenReturn(Optional.empty());
        when(progressRecordRepository.save(any(ProgressRecord.class)))
                .thenAnswer(inv -> inv.getArgument(0));

        ProgressRecord record = progressService.recordAssessmentProgress(athlete, squat, 80.0);

        assertEquals(1, record.getSessionNumber());
        assertEquals(80.0, record.getCurrentScore());
        assertEquals(0.0, record.getImprovementPercentage());
    }

    @Test
    void testLongitudinalImprovementCalculation() {
        // Equation (1.9.9): I = ((St - St-1) / St-1) * 100
        // Previous score St-1 = 80.0, New score St = 90.0
        // Expected improvement = ((90 - 80) / 80) * 100 = 12.5%
        AthleteProfile athlete = new AthleteProfile();
        athlete.setId(1L);
        SportsActivity squat = new SportsActivity("SQUAT", "Squat", "Squat Activity");

        ProgressRecord session1 = new ProgressRecord(athlete, squat, 1, 80.0, 80.0, 0.0);

        when(progressRecordRepository.findTopByAthleteAndSportsActivityOrderBySessionNumberDesc(athlete, squat))
                .thenReturn(Optional.of(session1));
        when(progressRecordRepository.save(any(ProgressRecord.class)))
                .thenAnswer(inv -> inv.getArgument(0));

        ProgressRecord session2 = progressService.recordAssessmentProgress(athlete, squat, 90.0);

        assertEquals(2, session2.getSessionNumber());
        assertEquals(90.0, session2.getCurrentScore());
        assertEquals(80.0, session2.getPreviousScore());
        assertEquals(12.5, session2.getImprovementPercentage(), 0.01);
    }
}
