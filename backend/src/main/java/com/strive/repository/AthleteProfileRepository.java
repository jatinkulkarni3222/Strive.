package com.strive.repository;

import com.strive.entity.AthleteProfile;
import com.strive.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AthleteProfileRepository extends JpaRepository<AthleteProfile, Long> {
    Optional<AthleteProfile> findByUser(User user);
    Optional<AthleteProfile> findByUserId(Long userId);
    List<AthleteProfile> findByGender(String gender);
    List<AthleteProfile> findByPrimarySport(String primarySport);

    @Query("SELECT p FROM AthleteProfile p WHERE " +
           "(:gender IS NULL OR p.gender = :gender) AND " +
           "(:primarySport IS NULL OR p.primarySport = :primarySport)")
    List<AthleteProfile> filterAthletes(@Param("gender") String gender, @Param("primarySport") String primarySport);
}
