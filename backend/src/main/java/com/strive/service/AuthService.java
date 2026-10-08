package com.strive.service;

import com.strive.config.JwtTokenProvider;
import com.strive.dto.AuthRequest;
import com.strive.dto.AuthResponse;
import com.strive.dto.RegisterRequest;
import com.strive.entity.AthleteProfile;
import com.strive.entity.Role;
import com.strive.entity.User;
import com.strive.exception.BadRequestException;
import com.strive.repository.AthleteProfileRepository;
import com.strive.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final AthleteProfileRepository athleteProfileRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider tokenProvider;

    public AuthService(UserRepository userRepository,
                       AthleteProfileRepository athleteProfileRepository,
                       PasswordEncoder passwordEncoder,
                       JwtTokenProvider tokenProvider) {
        this.userRepository = userRepository;
        this.athleteProfileRepository = athleteProfileRepository;
        this.passwordEncoder = passwordEncoder;
        this.tokenProvider = tokenProvider;
    }

    @Transactional
    public AuthResponse register(RegisterRequest request) {
        if (userRepository.existsByEmail(request.getEmail().toLowerCase())) {
            throw new BadRequestException("An account with email '" + request.getEmail() + "' already exists.");
        }

        User user = new User(
                request.getEmail().toLowerCase(),
                passwordEncoder.encode(request.getPassword()),
                request.getFullName(),
                request.getRole()
        );
        user = userRepository.save(user);

        Long athleteProfileId = null;
        if (user.getRole() == Role.ROLE_ATHLETE) {
            AthleteProfile profile = new AthleteProfile(
                    user,
                    request.getDateOfBirth(),
                    request.getGender() != null ? request.getGender().toUpperCase() : "MALE",
                    request.getHeightCm() != null ? request.getHeightCm() : 175.0,
                    request.getWeightKg() != null ? request.getWeightKg() : 70.0,
                    request.getCity(),
                    request.getState(),
                    request.getPrimarySport() != null ? request.getPrimarySport().toUpperCase() : "SQUAT"
            );
            profile = athleteProfileRepository.save(profile);
            athleteProfileId = profile.getId();
        }

        String token = tokenProvider.generateToken(user.getEmail(), user.getRole().name());
        return new AuthResponse(token, user.getId(), user.getEmail(), user.getFullName(), user.getRole(), athleteProfileId);
    }

    public AuthResponse login(AuthRequest request) {
        User user = userRepository.findByEmail(request.getEmail().toLowerCase())
                .orElseThrow(() -> new BadRequestException("Invalid email or password."));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new BadRequestException("Invalid email or password.");
        }

        Long athleteProfileId = null;
        if (user.getRole() == Role.ROLE_ATHLETE) {
            athleteProfileId = athleteProfileRepository.findByUser(user)
                    .map(AthleteProfile::getId)
                    .orElse(null);
        }

        String token = tokenProvider.generateToken(user.getEmail(), user.getRole().name());
        return new AuthResponse(token, user.getId(), user.getEmail(), user.getFullName(), user.getRole(), athleteProfileId);
    }
}
