package main

import (
	"time"
)

// SimulateStep runs one step of the simulation
func SimulateStep() error {
	// Load users from database
	users, err := loadUsersFromDB(config.NumUsersPerStep)
	if err != nil {
		return ErrSimulationStep(err)
	}

	// Load ads from database
	ads, err := loadAdsFromDB(config.NumAdsPerStep)
	if err != nil {
		return ErrSimulationStep(err)
	}

	// Process each user
	for _, user := range users {
		// Run ad auction
		selectedAds := runAuction(user, ads, 3)
		
		// Initialize simulation result
		result := SimulationResult{
			UserID:         user.ID,
			AdImpressions:  make([]AdImpression, 0),
			Reports:        make([]ContentReport, 0),
			Actions:        make([]ModerationAction, 0),
			Flags:          make([]ContentFlag, 0),
			Metrics:        make(map[string]float64),
			Timestamp:      time.Now(),
		}

		// Process selected ads
		for i, ad := range selectedAds {
			// Predict CTR
			ctr := PredictCTR(user, ad, i+1)
			
			// Determine if ad was clicked
			clicked := randomBool(ctr)
			
			// Record impression
			result.AdImpressions = append(result.AdImpressions, AdImpression{
				AdID:      ad.ID,
				Clicked:   clicked,
				Timestamp: time.Now(),
			})

			// Update user metrics based on click
			if clicked {
				user.ClicksLast24h++
				user.Satisfaction = clamp(user.Satisfaction+0.02, 0, 1)
				user.EngagementRate = clamp(user.EngagementRate+0.01, 0, 1)
			} else {
				user.Satisfaction = clamp(user.Satisfaction-0.01, 0, 1)
			}

			// Check for content reporting
			if shouldReportContent(user, ad) {
				report := generateContentReport(user, ad.ID, ContentTypeAd)
				result.Reports = append(result.Reports, report)

				// Generate moderation action
				action := generateModerationAction(report)
				result.Actions = append(result.Actions, action)

				// Generate content flag
				flag := generateContentFlag(ad.ID, ContentTypeAd)
				result.Flags = append(result.Flags, flag)
			}
		}

		// Simulate feed interaction
		contents, err := loadContentFromDB(config.NumContentPerStep)
		if err != nil {
			LogError("Failed to load content: %v", err)
			continue
		}

		// Track session start
		sessionStart := time.Now()

		for _, content := range contents {
			// Predict content interaction
			prediction := PredictContentInteraction(user, content)

			// Track content recommendation
			if err := trackContentRecommendation(user, content.ID, prediction.EngagementScore); err != nil {
				LogError("Failed to track content recommendation: %v", err)
			}

			// Determine if user interacts with content
			if randomBool(prediction.InteractionProb) {
				user.ContentInteractions++

				// Update video completion rate if applicable
				if content.ContentType == ContentTypeVideo {
					user.VideoCompletionRate = (user.VideoCompletionRate*float64(user.ContentInteractions) + prediction.CompletionProb) / float64(user.ContentInteractions+1)
				}

				// Check for content reporting
				if shouldReportContent(user, Ad{ID: content.ID, Category: rand.Intn(10)}) {
					report := generateContentReport(user, content.ID, content.ContentType)
					result.Reports = append(result.Reports, report)

					// Generate moderation action
					action := generateModerationAction(report)
					result.Actions = append(result.Actions, action)

					// Generate content flag
					flag := generateContentFlag(content.ID, content.ContentType)
					result.Flags = append(result.Flags, flag)
				}
			}
		}

		// Track session end
		sessionDuration := int(time.Since(sessionStart).Seconds())
		if err := trackUserSession(user, sessionDuration); err != nil {
			LogError("Failed to track user session: %v", err)
		}

		// Simulate network growth
		err = SimulateNetworkGrowth(user)
		if err != nil {
			LogError("Failed to simulate network growth: %v", err)
		}

		// Update user preferences and network metrics
		if err := updateUserPreferences(user); err != nil {
			LogError("Failed to update user preferences: %v", err)
		}
		if err := updateUserNetworkMetrics(user); err != nil {
			LogError("Failed to update user network metrics: %v", err)
		}

		// Check for user churn
		if SimulateUserChurn(user) {
			LogInfo("User %s churned with satisfaction %.2f", user.ID, user.Satisfaction)
			continue
		}

		// Update result metrics
		result.Metrics = map[string]float64{
			"satisfaction":        user.Satisfaction,
			"engagement_rate":     user.EngagementRate,
			"network_density":     user.NetworkDensity,
			"influence_score":     user.InfluenceScore,
			"scroll_depth":        user.AvgScrollDepth,
			"watch_time":          user.AvgWatchTime,
			"clicks":              float64(user.ClicksLast24h),
			"content_interactions": float64(user.ContentInteractions),
			"completion_rate":      user.VideoCompletionRate,
		}

		// Save simulation results
		err = saveSimulationResults(result)
		if err != nil {
			LogError("Failed to save simulation results: %v", err)
		}

		// Update metrics
		UpdateMetrics(func(m *Metrics) {
			m.TotalUsers++
			m.ActiveUsers++
			m.AverageSatisfaction += user.Satisfaction
			m.AverageEngagement += user.EngagementRate
			m.TotalContent += len(contents)
			m.TotalInteractions += user.ContentInteractions
			m.AverageCompletion += user.VideoCompletionRate
			m.TotalImpressions += len(result.AdImpressions)
			m.TotalClicks += user.ClicksLast24h
			m.TotalReports += len(result.Reports)
			m.TotalActions += len(result.Actions)
			m.ActiveFlags += len(result.Flags)
			m.TotalConnections += int(user.NetworkDensity * 100)
			m.AverageDensity += user.NetworkDensity
		})
	}

	return nil
}

// runAuction runs an ad auction for a user
func runAuction(user User, ads []Ad, numSlots int) []Ad {
	// Calculate scores for each ad
	type scoredAd struct {
		ad    Ad
		score float64
	}

	scoredAds := make([]scoredAd, len(ads))
	for i, ad := range ads {
		ctr := PredictCTR(user, ad, 1)
		quality := calculateQualityScore(user, ad)
		score := ctr * quality * ad.Bid
		scoredAds[i] = scoredAd{ad, score}
	}

	// Sort ads by score
	sort.Slice(scoredAds, func(i, j int) bool {
		return scoredAds[i].score > scoredAds[j].score
	})

	// Select top ads
	selected := make([]Ad, 0, numSlots)
	for i := 0; i < numSlots && i < len(scoredAds); i++ {
		selected = append(selected, scoredAds[i].ad)
	}

	return selected
}

// calculateQualityScore calculates the quality score for an ad
func calculateQualityScore(user User, ad Ad) float64 {
	score := 1.0

	// Adjust based on user preferences
	if preferences, ok := user.Preferences["categories"].([]interface{}); ok {
		for _, category := range preferences {
			if cat, ok := category.(float64); ok && int(cat) == ad.Category {
				score *= 1.2
				break
			}
		}
	}

	// Adjust based on target metrics
	for metric, target := range ad.TargetMetrics {
		switch metric {
		case "min_satisfaction":
			if user.Satisfaction < target {
				score *= 0.8
			}
		case "min_engagement":
			if user.EngagementRate < target {
				score *= 0.8
			}
		case "min_influence":
			if user.InfluenceScore < target {
				score *= 0.8
			}
		}
	}

	return score
} 