package com.strive.repository;

import com.strive.entity.Assessment;
import com.strive.entity.FeatureSet;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface FeatureSetRepository extends JpaRepository<FeatureSet, Long> {
    Optional<FeatureSet> findByAssessment(Assessment assessment);
}
