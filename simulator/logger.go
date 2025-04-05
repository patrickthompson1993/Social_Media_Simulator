package main

import (
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"time"
)

var (
	infoLogger  *log.Logger
	errorLogger *log.Logger
	logFile     *os.File
)

// InitLogger initializes the logging system
func InitLogger(logDir string) error {
	// Create log directory if it doesn't exist
	if err := os.MkdirAll(logDir, 0755); err != nil {
		return fmt.Errorf("failed to create log directory: %v", err)
	}
	
	// Create log file with timestamp
	timestamp := time.Now().Format("2006-01-02_15-04-05")
	logPath := filepath.Join(logDir, fmt.Sprintf("simulator_%s.log", timestamp))
	
	var err error
	logFile, err = os.OpenFile(logPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		return fmt.Errorf("failed to open log file: %v", err)
	}
	
	// Initialize loggers
	infoLogger = log.New(logFile, "INFO: ", log.Ldate|log.Ltime|log.Lshortfile)
	errorLogger = log.New(logFile, "ERROR: ", log.Ldate|log.Ltime|log.Lshortfile)
	
	// Also log to stdout
	infoLogger.SetOutput(io.MultiWriter(os.Stdout, logFile))
	errorLogger.SetOutput(io.MultiWriter(os.Stderr, logFile))
	
	return nil
}

// CloseLogger closes the log file
func CloseLogger() {
	if logFile != nil {
		logFile.Close()
	}
}

// LogInfo logs an info message
func LogInfo(format string, v ...interface{}) {
	infoLogger.Printf(format, v...)
}

// LogError logs an error message
func LogError(format string, v ...interface{}) {
	errorLogger.Printf(format, v...)
}

// LogSimulationStep logs information about a simulation step
func LogSimulationStep(step int, totalSteps int, duration time.Duration) {
	LogInfo("Step %d/%d completed in %v", step, totalSteps, duration)
	LogMetrics()
}

// LogUserAction logs a user action
func LogUserAction(userID string, action string, details ...interface{}) {
	format := fmt.Sprintf("User %s: %s", userID, action)
	LogInfo(format, details...)
}

// LogContentAction logs a content-related action
func LogContentAction(contentID string, action string, details ...interface{}) {
	format := fmt.Sprintf("Content %s: %s", contentID, action)
	LogInfo(format, details...)
}

// LogModerationAction logs a moderation action
func LogModerationAction(reportID string, action string, details ...interface{}) {
	format := fmt.Sprintf("Moderation %s: %s", reportID, action)
	LogInfo(format, details...)
}

// LogAdAction logs an ad-related action
func LogAdAction(adID string, action string, details ...interface{}) {
	format := fmt.Sprintf("Ad %s: %s", adID, action)
	LogInfo(format, details...)
}

// LogNetworkAction logs a network-related action
func LogNetworkAction(userID string, action string, details ...interface{}) {
	format := fmt.Sprintf("Network %s: %s", userID, action)
	LogInfo(format, details...)
} 