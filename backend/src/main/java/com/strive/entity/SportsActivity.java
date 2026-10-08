package com.strive.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "sports_activities")
public class SportsActivity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String code; // SQUAT, PUSHUP, VERTICAL_JUMP

    @Column(nullable = false)
    private String name;

    private String description;

    public SportsActivity() {}

    public SportsActivity(String code, String name, String description) {
        this.code = code;
        this.name = name;
        this.description = description;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
}
