package com.strive;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.security.servlet.UserDetailsServiceAutoConfiguration;

@SpringBootApplication(exclude = { UserDetailsServiceAutoConfiguration.class })
public class StriveApplication {

    public static void main(String[] args) {
        SpringApplication.run(StriveApplication.class, args);
    }
}
