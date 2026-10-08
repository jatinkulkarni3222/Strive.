package com.strive.repository;

import com.strive.entity.AthleteProfile;
import com.strive.entity.Video;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface VideoRepository extends JpaRepository<Video, Long> {
    List<Video> findByAthleteOrderByUploadedAtDesc(AthleteProfile athlete);
}
