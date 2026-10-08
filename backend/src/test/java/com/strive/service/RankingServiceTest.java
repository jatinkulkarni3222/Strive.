package com.strive.service;

import com.strive.entity.AthleteProfile;
import com.strive.entity.Ranking;
import com.strive.entity.SportsActivity;
import com.strive.entity.User;
import com.strive.repository.RankingRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class RankingServiceTest {

    @Mock
    private RankingRepository rankingRepository;

    private RankingService rankingService;

    @BeforeEach
    void setUp() {
        rankingService = new RankingService(rankingRepository);
    }

    @Test
    void testCohortRankingAssignment() {
        SportsActivity squat = new SportsActivity("SQUAT", "Squat", "Squat Activity");

        AthleteProfile a1 = new AthleteProfile();
        a1.setId(1L);
        a1.setUser(new User("a1@strive.org", "pwd", "Athlete One", null));

        AthleteProfile a2 = new AthleteProfile();
        a2.setId(2L);
        a2.setUser(new User("a2@strive.org", "pwd", "Athlete Two", null));

        Ranking r1 = new Ranking(a1, squat, 95.0, 1, "SENIOR", "MALE");
        Ranking r2 = new Ranking(a2, squat, 85.0, 2, "SENIOR", "MALE");

        List<Ranking> list = new ArrayList<>(List.of(r2, r1)); // unsorted
        when(rankingRepository.findByAthleteIdAndSportsActivity(a1.getId(), squat)).thenReturn(Optional.of(r1));
        when(rankingRepository.findBySportsActivityOrderByRankPositionAsc(squat)).thenReturn(list);

        rankingService.updateAthleteRanking(a1, squat, 96.0);

        // After re-ranking, r1 (score 96) must be rank 1, and r2 (score 85) must be rank 2
        assertEquals(1, r1.getRankPosition());
        assertEquals(2, r2.getRankPosition());
        verify(rankingRepository).saveAll(any());
    }
}
