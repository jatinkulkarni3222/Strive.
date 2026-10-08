package com.strive.entity;

import jakarta.persistence.*;
import java.time.LocalDate;
import java.time.Period;

@Entity
@Table(name = "athlete_profiles")
public class AthleteProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "user_id", nullable = false, unique = true)
    private User user;

    private LocalDate dateOfBirth;
    private String gender; // MALE, FEMALE, OTHER
    private Double heightCm;
    private Double weightKg;
    private String city;
    private String state;
    private String primarySport;

    public AthleteProfile() {}

    public AthleteProfile(User user, LocalDate dateOfBirth, String gender, Double heightCm, Double weightKg, String city, String state, String primarySport) {
        this.user = user;
        this.dateOfBirth = dateOfBirth;
        this.gender = gender;
        this.heightCm = heightCm;
        this.weightKg = weightKg;
        this.city = city;
        this.state = state;
        this.primarySport = primarySport;
    }

    public int getAge() {
        if (dateOfBirth == null) return 20;
        return Period.between(dateOfBirth, LocalDate.now()).getYears();
    }

    public String getAgeGroup() {
        int age = getAge();
        if (age < 17) return "U-17";
        if (age < 21) return "U-21";
        return "SENIOR";
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }

    public LocalDate getDateOfBirth() { return dateOfBirth; }
    public void setDateOfBirth(LocalDate dateOfBirth) { this.dateOfBirth = dateOfBirth; }

    public String getGender() { return gender; }
    public void setGender(String gender) { this.gender = gender; }

    public Double getHeightCm() { return heightCm; }
    public void setHeightCm(Double heightCm) { this.heightCm = heightCm; }

    public Double getWeightKg() { return weightKg; }
    public void setWeightKg(Double weightKg) { this.weightKg = weightKg; }

    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }

    public String getState() { return state; }
    public void setState(String state) { this.state = state; }

    public String getPrimarySport() { return primarySport; }
    public void setPrimarySport(String primarySport) { this.primarySport = primarySport; }
}
