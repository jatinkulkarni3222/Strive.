package com.strive.config;

import com.strive.entity.*;
import com.strive.repository.*;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.time.LocalDate;

@Component
public class DataInitializer implements CommandLineRunner {

    private final SportsActivityRepository sportsActivityRepository;
    private final UserRepository userRepository;
    private final AthleteProfileRepository athleteProfileRepository;
    private final CoachAthleteMappingRepository mappingRepository;
    private final RankingRepository rankingRepository;
    private final PasswordEncoder passwordEncoder;

    public DataInitializer(SportsActivityRepository sportsActivityRepository,
                           UserRepository userRepository,
                           AthleteProfileRepository athleteProfileRepository,
                           CoachAthleteMappingRepository mappingRepository,
                           RankingRepository rankingRepository,
                           PasswordEncoder passwordEncoder) {
        this.sportsActivityRepository = sportsActivityRepository;
        this.userRepository = userRepository;
        this.athleteProfileRepository = athleteProfileRepository;
        this.mappingRepository = mappingRepository;
        this.rankingRepository = rankingRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) {
        // 1. Seed Sports Activities
        if (sportsActivityRepository.count() == 0) {
            sportsActivityRepository.save(new SportsActivity("SQUAT", "Bodyweight / Back Squat", "Bilateral knee and hip flexion evaluating lower body strength and trunk control"));
            sportsActivityRepository.save(new SportsActivity("PUSHUP", "Push-Up", "Horizontal pressing assessing upper body endurance and core plank stability"));
            sportsActivityRepository.save(new SportsActivity("VERTICAL_JUMP", "Vertical Jump", "Explosive triple extension assessing power output and landing mechanics"));
        }

        // 2. Seed Default Demo Users if none exist
        if (userRepository.count() == 0) {
            String defaultPwd = passwordEncoder.encode("Strive@2026");

            // Athlete 1: Vedant Patil
            User u1 = userRepository.save(new User("athlete@strive.org", defaultPwd, "Vedant Patil", Role.ROLE_ATHLETE));
            AthleteProfile a1 = athleteProfileRepository.save(new AthleteProfile(
                    u1, LocalDate.of(2004, 5, 14), "MALE", 178.0, 72.5, "Pune", "Maharashtra", "SQUAT"));

            // Athlete 2: Neha Sharma
            User u2 = userRepository.save(new User("neha@strive.org", defaultPwd, "Neha Sharma", Role.ROLE_ATHLETE));
            AthleteProfile a2 = athleteProfileRepository.save(new AthleteProfile(
                    u2, LocalDate.of(2006, 9, 21), "FEMALE", 165.0, 58.0, "Satara", "Maharashtra", "SQUAT"));

            // Athlete 3: Rahul Deshmukh
            User u3 = userRepository.save(new User("rahul@strive.org", defaultPwd, "Rahul Deshmukh", Role.ROLE_ATHLETE));
            AthleteProfile a3 = athleteProfileRepository.save(new AthleteProfile(
                    u3, LocalDate.of(2008, 1, 10), "MALE", 172.0, 64.0, "Kolhapur", "Maharashtra", "SQUAT"));

            // Coach: Rutuja Magar
            User coach = userRepository.save(new User("coach@strive.org", defaultPwd, "Coach Rutuja Magar", Role.ROLE_COACH));
            mappingRepository.save(new CoachAthleteMapping(coach, a1, "Solid squat depth. Needs to focus on knee tracking over toes to prevent inward valgus."));
            mappingRepository.save(new CoachAthleteMapping(coach, a2, "Excellent trunk stability and posture consistency."));

            // Scout: Vijay Kotkar
            User scout = userRepository.save(new User("scout@strive.org", defaultPwd, "Scout Vijay Kotkar", Role.ROLE_SCOUT));

            // Initial Rankings
            SportsActivity squatAct = sportsActivityRepository.findByCode("SQUAT").orElse(null);
            if (squatAct != null) {
                rankingRepository.save(new Ranking(a1, squatAct, 90.0, 1, a1.getAgeGroup(), a1.getGender()));
                rankingRepository.save(new Ranking(a2, squatAct, 88.5, 2, a2.getAgeGroup(), a2.getGender()));
                rankingRepository.save(new Ranking(a3, squatAct, 79.0, 3, a3.getAgeGroup(), a3.getGender()));
            }
        }
    }
}
