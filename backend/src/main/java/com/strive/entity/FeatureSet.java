package com.strive.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "feature_sets")
public class FeatureSet {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "assessment_id", nullable = false, unique = true)
    private Assessment assessment;

    private Double avgRom;
    private Double consistencyScore;
    private Double peakVelocity;
    private Double peakAcceleration;

    @Column(length = 2000)
    private String featureVectorJson;

    public FeatureSet() {}

    public FeatureSet(Assessment assessment, Double avgRom, Double consistencyScore,
                      Double peakVelocity, Double peakAcceleration, String featureVectorJson) {
        this.assessment = assessment;
        this.avgRom = avgRom;
        this.consistencyScore = consistencyScore;
        this.peakVelocity = peakVelocity;
        this.peakAcceleration = peakAcceleration;
        this.featureVectorJson = featureVectorJson;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Assessment getAssessment() { return assessment; }
    public void setAssessment(Assessment assessment) { this.assessment = assessment; }

    public Double getAvgRom() { return avgRom; }
    public void setAvgRom(Double avgRom) { this.avgRom = avgRom; }

    public Double getConsistencyScore() { return consistencyScore; }
    public void setConsistencyScore(Double consistencyScore) { this.consistencyScore = consistencyScore; }

    public Double getPeakVelocity() { return peakVelocity; }
    public void setPeakVelocity(Double peakVelocity) { this.peakVelocity = peakVelocity; }

    public Double getPeakAcceleration() { return peakAcceleration; }
    public void setPeakAcceleration(Double peakAcceleration) { this.peakAcceleration = peakAcceleration; }

    public String getFeatureVectorJson() { return featureVectorJson; }
    public void setFeatureVectorJson(String featureVectorJson) { this.featureVectorJson = featureVectorJson; }
}
