package com.strive.service;

import com.strive.exception.CvProcessingException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Map;

@Service
public class CvClientService {

    private final RestTemplate restTemplate;
    private final String cvServiceUrl;

    public CvClientService(@Value("${cv.service.url:http://localhost:8000}") String cvServiceUrl) {
        this.restTemplate = new RestTemplate();
        this.cvServiceUrl = cvServiceUrl;
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> analyzeVideo(MultipartFile videoFile, String sportCode) {
        String url = cvServiceUrl + "/analyze";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        try {
            ByteArrayResource fileResource = new ByteArrayResource(videoFile.getBytes()) {
                @Override
                public String getFilename() {
                    return videoFile.getOriginalFilename() != null ? videoFile.getOriginalFilename() : "video.mp4";
                }
            };
            body.add("video", fileResource);
        } catch (IOException e) {
            throw new CvProcessingException("Could not read uploaded video bytes: " + e.getMessage());
        }

        body.add("sport", sportCode.toLowerCase());

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

        try {
            ResponseEntity<Map> response = restTemplate.postForEntity(url, requestEntity, Map.class);
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return (Map<String, Object>) response.getBody();
            } else {
                throw new CvProcessingException("CV service returned non-200 status: " + response.getStatusCode());
            }
        } catch (RestClientException e) {
            throw new CvProcessingException("Failed to communicate with Computer Vision service: " + e.getMessage());
        }
    }
}
