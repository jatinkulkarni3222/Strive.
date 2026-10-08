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
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.LocalDate;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class AuthServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private AthleteProfileRepository athleteProfileRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private JwtTokenProvider tokenProvider;

    private AuthService authService;

    @BeforeEach
    void setUp() {
        authService = new AuthService(userRepository, athleteProfileRepository, passwordEncoder, tokenProvider);
    }

    @Test
    void testRegisterAthleteSuccess() {
        RegisterRequest req = new RegisterRequest();
        req.setEmail("athlete@test.com");
        req.setPassword("Secret123");
        req.setFullName("John Doe");
        req.setRole(Role.ROLE_ATHLETE);
        req.setDateOfBirth(LocalDate.of(2005, 1, 1));
        req.setGender("MALE");
        req.setCity("Pune");
        req.setState("Maharashtra");
        req.setPrimarySport("SQUAT");

        when(userRepository.existsByEmail("athlete@test.com")).thenReturn(false);
        when(passwordEncoder.encode("Secret123")).thenReturn("encodedPassword");

        User savedUser = new User("athlete@test.com", "encodedPassword", "John Doe", Role.ROLE_ATHLETE);
        savedUser.setId(10L);
        when(userRepository.save(any(User.class))).thenReturn(savedUser);

        AthleteProfile savedProfile = new AthleteProfile(savedUser, req.getDateOfBirth(), "MALE", 175.0, 70.0, "Pune", "Maharashtra", "SQUAT");
        savedProfile.setId(20L);
        when(athleteProfileRepository.save(any(AthleteProfile.class))).thenReturn(savedProfile);

        when(tokenProvider.generateToken("athlete@test.com", "ROLE_ATHLETE")).thenReturn("jwt_mock_token");

        AuthResponse resp = authService.register(req);

        assertNotNull(resp);
        assertEquals("jwt_mock_token", resp.getToken());
        assertEquals(10L, resp.getUserId());
        assertEquals(20L, resp.getAthleteProfileId());
        assertEquals("athlete@test.com", resp.getEmail());
    }

    @Test
    void testRegisterDuplicateEmailThrows() {
        RegisterRequest req = new RegisterRequest();
        req.setEmail("duplicate@test.com");
        when(userRepository.existsByEmail("duplicate@test.com")).thenReturn(true);

        assertThrows(BadRequestException.class, () -> authService.register(req));
        verify(userRepository, never()).save(any());
    }

    @Test
    void testLoginSuccess() {
        AuthRequest req = new AuthRequest("user@test.com", "validPassword");
        User user = new User("user@test.com", "encodedValidPassword", "User Name", Role.ROLE_COACH);
        user.setId(5L);

        when(userRepository.findByEmail("user@test.com")).thenReturn(Optional.of(user));
        when(passwordEncoder.matches("validPassword", "encodedValidPassword")).thenReturn(true);
        when(tokenProvider.generateToken("user@test.com", "ROLE_COACH")).thenReturn("jwt_token_123");

        AuthResponse resp = authService.login(req);

        assertEquals("jwt_token_123", resp.getToken());
        assertEquals(Role.ROLE_COACH, resp.getRole());
    }
}
