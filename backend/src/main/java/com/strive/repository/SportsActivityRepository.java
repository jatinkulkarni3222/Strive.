package com.strive.repository;

import com.strive.entity.SportsActivity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface SportsActivityRepository extends JpaRepository<SportsActivity, Long> {
    Optional<SportsActivity> findByCode(String code);
}
