package main

import (
	"fmt"
	"time"
)

// SimulatorError represents an error that occurred during simulation
type SimulatorError struct {
	Time      time.Time
	Component string
	Operation string
	Message   string
	Err       error
}

func (e *SimulatorError) Error() string {
	return fmt.Sprintf("[%s] %s.%s: %s (caused by: %v)", 
		e.Time.Format(time.RFC3339), 
		e.Component, 
		e.Operation, 
		e.Message, 
		e.Err,
	)
}

// NewSimulatorError creates a new simulator error
func NewSimulatorError(component, operation, message string, err error) *SimulatorError {
	return &SimulatorError{
		Time:      time.Now(),
		Component: component,
		Operation: operation,
		Message:   message,
		Err:       err,
	}
}

// Error types
var (
	ErrDatabaseConnection = func(err error) *SimulatorError {
		return NewSimulatorError("Database", "Connection", "Failed to connect to database", err)
	}
	
	ErrDatabaseQuery = func(operation string, err error) *SimulatorError {
		return NewSimulatorError("Database", operation, "Database query failed", err)
	}
	
	ErrModelPrediction = func(model string, err error) *SimulatorError {
		return NewSimulatorError("Model", model, "Prediction failed", err)
	}
	
	ErrUserGeneration = func(err error) *SimulatorError {
		return NewSimulatorError("User", "Generation", "Failed to generate user", err)
	}
	
	ErrContentGeneration = func(err error) *SimulatorError {
		return NewSimulatorError("Content", "Generation", "Failed to generate content", err)
	}
	
	ErrAdGeneration = func(err error) *SimulatorError {
		return NewSimulatorError("Ad", "Generation", "Failed to generate ad", err)
	}
	
	ErrReportGeneration = func(err error) *SimulatorError {
		return NewSimulatorError("Report", "Generation", "Failed to generate report", err)
	}
	
	ErrModerationAction = func(err error) *SimulatorError {
		return NewSimulatorError("Moderation", "Action", "Failed to generate moderation action", err)
	}
	
	ErrFlagGeneration = func(err error) *SimulatorError {
		return NewSimulatorError("Flag", "Generation", "Failed to generate flag", err)
	}
	
	ErrMetricsUpdate = func(err error) *SimulatorError {
		return NewSimulatorError("Metrics", "Update", "Failed to update metrics", err)
	}
	
	ErrSimulationStep = func(err error) *SimulatorError {
		return NewSimulatorError("Simulation", "Step", "Failed to execute simulation step", err)
	}
)

// HandleError handles a simulator error
func HandleError(err error) {
	if err == nil {
		return
	}
	
	if simErr, ok := err.(*SimulatorError); ok {
		LogError("%v", simErr)
	} else {
		LogError("Unexpected error: %v", err)
	}
} 