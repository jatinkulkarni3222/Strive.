package com.strive.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.strive.dto.AssessmentResponse;
import com.strive.entity.*;
import com.strive.exception.BadRequestException;
import com.strive.exception.ResourceNotFoundException;
import com.strive.repository.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class VideoAssessmentService {

    private final VideoRepository videoRepository;
    private final AssessmentRepository assessmentRepository;
    private final FeatureSetRepository featureSetRepository;
    private final AthleteProfileRepository athleteProfileRepository;
    private final SportsActivityRepository sportsActivityRepository;
    private final CvClientService cvClientService;
    private final ProgressService progressService;
    private final RankingService rankingService;
    private final ObjectMapper objectMapper;
    private final Path storageLocation;

    public VideoAssessmentService(
            VideoRepository videoRepository,
            AssessmentRepository assessmentRepository,
            FeatureSetRepository featureSetRepository,
            AthleteProfileRepository athleteProfileRepository,
            SportsActivityRepository sportsActivityRepository,
            CvClientService cvClientService,
            ProgressService progressService,
            RankingService rankingService,
            @Value("${storage.location:./storage/uploads}") String storageLocation) {
        this.videoRepository = videoRepository;
        this.assessmentRepository = assessmentRepository;
        this.featureSetRepository = featureSetRepository;
        this.athleteProfileRepository = athleteProfileRepository;
        this.sportsActivityRepository = sportsActivityRepository;
        this.cvClientService = cvClientService;
        this.progressService = progressService;
        this.rankingService = rankingService;
        this.objectMapper = new ObjectMapper();
        this.storageLocation = Paths.get(storageLocation).toAbsolutePath().normalize();

        try {
            Files.createDirectories(this.storageLocation);
        } catch (IOException e) {
            // Log directory creation warning
        }
    }

    @Transactional
    public AssessmentResponse processVideoAssessment(Long athleteProfileId, String sportCode, MultipartFile file) {
        if (file.isEmpty()) {
            throw new BadRequestException("Uploaded video file cannot be empty.");
        }

        AthleteProfile athlete = athleteProfileRepository.findById(athleteProfileId)
                .orElseThrow(() -> new ResourceNotFoundException("Athlete profile not found with ID: " + athleteProfileId));

        SportsActivity sportsActivity = sportsActivityRepository.findByCode(sportCode.toUpperCase())
                .orElseThrow(() -> new ResourceNotFoundException("Sport activity not found: " + sportCode));

        // Save raw video locally
        String originalFilename = file.getOriginalFilename() != null ? file.getOriginalFilename() : "upload.mp4";
        String storedFilename = UUID.randomUUID().toString() + "_" + originalFilename;
        Path targetPath = this.storageLocation.resolve(storedFilename);

        try {
            Files.copy(file.getInputStream(), targetPath, StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException e) {
            throw new BadRequestException("Could not persist video file: " + e.getMessage());
        }

        Video video = new Video(athlete, sportsActivity, originalFilename, targetPath.toString());
        video = videoRepository.save(video);

        // Forward to CV Service
        Map<String, Object> cvResult = cvClientService.analyzeVideo(file, sportsActivity.getCode());

        // Extract CV outputs
        Double performanceScore = ((Number) cvResult.getOrDefault("performance_score", 0.0)).doubleValue();
        Double confidenceScore = ((Number) cvResult.getOrDefault("confidence_score", 1.0)).doubleValue();
        Double movementDeviation = ((Number) cvResult.getOrDefault("movement_deviation", 0.0)).doubleValue();
        Integer repCount = ((Number) cvResult.getOrDefault("rep_count", 0)).intValue();
        String injuryRiskLevel = (String) cvResult.getOrDefault("injury_risk_level", "LOW");
        String annotatedUrl = (String) cvResult.getOrDefault("annotated_video_url", "");

        String injuryInsightsJson = "";
        try {
            injuryInsightsJson = objectMapper.writeValueAsString(cvResult.get("injury_insights"));
        } catch (JsonProcessingException e) {
            injuryInsightsJson = "[]";
        }

        video.setAnnotatedPath(annotatedUrl);
        video.setStatus("ANALYZED");
        videoRepository.save(video);

        Assessment assessment = new Assessment(
                video,
                athlete,
                sportsActivity,
                performanceScore,
                confidenceScore,
                movementDeviation,
                repCount,
                injuryRiskLevel,
                injuryInsightsJson
        );
        assessment = assessmentRepository.save(assessment);

        // Save FeatureSet
        @SuppressWarnings("unchecked")
        Map<String, Object> subScores = (Map<String, Object>) cvResult.get("sub_scores");
        Double rom = subScores != null ? ((Number) subScores.getOrDefault("range_of_motion", 0.0)).doubleValue() : 0.0;
        Double consistency = subScores != null ? ((Number) subScores.getOrDefault("consistency", 0.0)).doubleValue() : 0.0;

        String featureVectorJson = "";
        try {
            featureVectorJson = objectMapper.writeValueAsString(cvResult.get("feature_vector"));
        } catch (JsonProcessingException e) {
            featureVectorJson = "[]";
        }

        FeatureSet featureSet = new FeatureSet(assessment, rom, consistency, 0.0, 0.0, featureVectorJson);
        featureSetRepository.save(featureSet);

        // Update Longitudinal Progress Record (Equation 1.9.9)
        progressService.recordAssessmentProgress(athlete, sportsActivity, performanceScore);

        // Update Athlete Ranking (Equation 1.9.10)
        rankingService.updateAthleteRanking(athlete, sportsActivity, performanceScore);

        return mapToResponse(assessment);
    }

    public AssessmentResponse getAssessmentById(Long assessmentId) {
        Assessment assessment = assessmentRepository.findById(assessmentId)
                .orElseThrow(() -> new ResourceNotFoundException("Assessment not found with ID: " + assessmentId));
        return mapToResponse(assessment);
    }

    public List<AssessmentResponse> getAthleteAssessments(Long athleteProfileId) {
        AthleteProfile athlete = athleteProfileRepository.findById(athleteProfileId)
                .orElseThrow(() -> new ResourceNotFoundException("Athlete profile not found with ID: " + athleteProfileId));
        return assessmentRepository.findByAthleteOrderByAssessedAtDesc(athlete).stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    private AssessmentResponse mapToResponse(Assessment a) {
        AssessmentResponse dto = new AssessmentResponse();
        dto.setId(a.getId());
        dto.setVideoId(a.getVideo().getId());
        dto.setAthleteId(a.getAthlete().getId());
        dto.setAthleteName(a.getAthlete().getUser().getFullName());
        dto.setSportCode(a.getSportsActivity().getCode());
        dto.setSportName(a.getSportsActivity().getName());
        dto.setScore(a.getScore());
        dto.setConfidenceScore(a.getConfidenceScore());
        dto.setMovementDeviation(a.getMovementDeviation());
        dto.setRepCount(a.getRepCount());
        dto.setInjuryRiskLevel(a.getInjuryRiskLevel());
        dto.setInjuryInsights(a.getInjuryInsights());
        dto.setAnnotatedVideoUrl(a.getVideo().getAnnotatedPath());
        dto.setAssessedAt(a.getAssessedAt());
        return dto;
    }
}
