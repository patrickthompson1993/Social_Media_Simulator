package main

import (
	"sync"
	"time"
)

// Metrics tracks various simulation metrics
type Metrics struct {
	mu sync.RWMutex
	
	// User metrics
	TotalUsers          int
	ActiveUsers         int
	ChurnedUsers        int
	AverageSatisfaction float64
	AverageEngagement   float64
	
	// Content metrics
	TotalContent        int
	TotalInteractions   int
	AverageCompletion   float64
	ReportedContent     int
	
	// Ad metrics
	TotalImpressions    int
	TotalClicks         int
	AverageCTR          float64
	TotalSpend          float64
	
	// Moderation metrics
	TotalReports        int
	TotalActions        int
	ActiveFlags         int
	
	// Network metrics
	TotalConnections    int
	AverageDensity      float64
	
	// Timing metrics
	StartTime           time.Time
	LastUpdateTime      time.Time
}

var metrics = &Metrics{
	StartTime: time.Now(),
}

// UpdateMetrics updates the metrics with new simulation data
func UpdateMetrics(update func(*Metrics)) {
	metrics.mu.Lock()
	defer metrics.mu.Unlock()
	
	update(metrics)
	metrics.LastUpdateTime = time.Now()
}

// GetMetrics returns a copy of the current metrics
func GetMetrics() Metrics {
	metrics.mu.RLock()
	defer metrics.mu.RUnlock()
	
	return *metrics
}

// ResetMetrics resets all metrics to their initial values
func ResetMetrics() {
	metrics.mu.Lock()
	defer metrics.mu.Unlock()
	
	*metrics = Metrics{
		StartTime: time.Now(),
	}
}

// CalculateMetrics calculates derived metrics
func (m *Metrics) CalculateMetrics() {
	// Calculate averages
	if m.TotalUsers > 0 {
		m.AverageSatisfaction = m.AverageSatisfaction / float64(m.TotalUsers)
		m.AverageEngagement = m.AverageEngagement / float64(m.TotalUsers)
		m.AverageDensity = m.AverageDensity / float64(m.TotalUsers)
	}
	
	if m.TotalImpressions > 0 {
		m.AverageCTR = float64(m.TotalClicks) / float64(m.TotalImpressions)
	}
	
	if m.TotalContent > 0 {
		m.AverageCompletion = m.AverageCompletion / float64(m.TotalContent)
	}
}

// LogMetrics logs the current metrics
func LogMetrics() {
	m := GetMetrics()
	m.CalculateMetrics()
	
	log.Printf("Simulation Metrics:")
	log.Printf("  Users: Total=%d, Active=%d, Churned=%d", m.TotalUsers, m.ActiveUsers, m.ChurnedUsers)
	log.Printf("  Satisfaction: %.2f, Engagement: %.2f", m.AverageSatisfaction, m.AverageEngagement)
	log.Printf("  Content: Total=%d, Interactions=%d, Reported=%d", m.TotalContent, m.TotalInteractions, m.ReportedContent)
	log.Printf("  Ads: Impressions=%d, Clicks=%d, CTR=%.2f%%, Spend=%.2f", 
		m.TotalImpressions, m.TotalClicks, m.AverageCTR*100, m.TotalSpend)
	log.Printf("  Moderation: Reports=%d, Actions=%d, Active Flags=%d", 
		m.TotalReports, m.TotalActions, m.ActiveFlags)
	log.Printf("  Network: Connections=%d, Avg Density=%.2f", m.TotalConnections, m.AverageDensity)
	log.Printf("  Runtime: %v", time.Since(m.StartTime))
} 