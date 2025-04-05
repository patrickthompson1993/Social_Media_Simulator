package main

import (
	"os"
	"strconv"
)

// Config holds all configuration for the simulator
type Config struct {
	// Database configuration
	DatabaseURL string
	
	// Simulation parameters
	NumUsersPerStep    int
	NumAdsPerStep      int
	NumContentPerStep  int
	StepInterval       int // in seconds
	
	// API endpoints
	APIBaseURL          string
	CTREndpoint          string
	ContentEndpoint      string
	FeedRankingEndpoint  string
	ModerationEndpoint   string
	
	// Simulation probabilities
	ReportProbability    float64
	ChurnBaseProbability float64
	InteractionBaseProbability float64
}

// LoadConfig loads configuration from environment variables with defaults
func LoadConfig() *Config {
	apiBaseURL := getEnvOrDefault("API_BASE_URL", "http://localhost:8000")
	
	config := &Config{
		// Database defaults
		DatabaseURL: getEnvOrDefault("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/socialmedia?sslmode=disable"),
		
		// Simulation parameters defaults
		NumUsersPerStep:    getEnvIntOrDefault("NUM_USERS_PER_STEP", 5),
		NumAdsPerStep:      getEnvIntOrDefault("NUM_ADS_PER_STEP", 10),
		NumContentPerStep:  getEnvIntOrDefault("NUM_CONTENT_PER_STEP", 10),
		StepInterval:       getEnvIntOrDefault("STEP_INTERVAL", 1),
		
		// API endpoints defaults
		APIBaseURL:          apiBaseURL,
		CTREndpoint:         getEnvOrDefault("CTR_ENDPOINT", apiBaseURL+"/api/ads/predict/ctr"),
		ContentEndpoint:     getEnvOrDefault("CONTENT_ENDPOINT", apiBaseURL+"/api/content/predict"),
		FeedRankingEndpoint: getEnvOrDefault("FEED_RANKING_ENDPOINT", apiBaseURL+"/api/content/predict/feed"),
		ModerationEndpoint:  getEnvOrDefault("MODERATION_ENDPOINT", apiBaseURL+"/api/moderation/predict"),
		
		// Simulation probabilities defaults
		ReportProbability:    getEnvFloatOrDefault("REPORT_PROBABILITY", 0.1),
		ChurnBaseProbability: getEnvFloatOrDefault("CHURN_BASE_PROBABILITY", 0.01),
		InteractionBaseProbability: getEnvFloatOrDefault("INTERACTION_BASE_PROBABILITY", 0.3),
	}
	
	return config
}

// Helper functions to get environment variables with defaults
func getEnvOrDefault(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvIntOrDefault(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func getEnvFloatOrDefault(key string, defaultValue float64) float64 {
	if value := os.Getenv(key); value != "" {
		if floatValue, err := strconv.ParseFloat(value, 64); err == nil {
			return floatValue
		}
	}
	return defaultValue
} 