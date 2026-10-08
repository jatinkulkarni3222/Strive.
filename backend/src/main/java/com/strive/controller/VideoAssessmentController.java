package com.strive.controller;

import com.strive.dto.AssessmentResponse;
import com.strive.service.VideoAssessmentService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/api/assessments")
@Tag(name = "Assessments", description = "Video upload, Computer Vision processing, and result retrieval")
public class VideoAssessmentController {

    private final VideoAssessmentService videoAssessmentService;

    public VideoAssessmentController(VideoAssessmentService videoAssessmentService) {
        this.videoAssessmentService = videoAssessmentService;
    }

    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @Operation(summary = "Upload athlete movement video and trigger CV assessment")
    public ResponseEntity<AssessmentResponse> uploadAndAssess(
            @RequestParam("athleteId") Long athleteId,
            @RequestParam("sport") String sport,
            @RequestParam("video") MultipartFile video) {
        AssessmentResponse response = videoAssessmentService.processVideoAssessment(athleteId, sport, video);
        return new ResponseEntity<>(response, HttpStatus.CREATED);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get biomechanical assessment result by ID")
    public ResponseEntity<AssessmentResponse> getAssessmentById(@PathVariable("id") Long id) {
        return ResponseEntity.ok(videoAssessmentService.getAssessmentById(id));
    }

    @GetMapping("/athlete/{athleteId}")
    @Operation(summary = "Get historical assessments for an athlete")
    public ResponseEntity<List<AssessmentResponse>> getAthleteAssessments(@PathVariable("athleteId") Long athleteId) {
        return ResponseEntity.ok(videoAssessmentService.getAthleteAssessments(athleteId));
    }
}
