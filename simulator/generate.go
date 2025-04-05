package main

import (
	"time"
)

// generateUser generates a new user
func generateUser() User {
	user := User{
		ID:                  randomString(8),
		Username:            generateUsername(),
		Email:               generateEmail(),
		Age:                 randomInt(18, 65),
		Gender:              randomChoice([]string{"male", "female", "non-binary", "other"}),
		EyeColor:            randomChoice([]string{"blue", "brown", "green", "hazel", "gray", "other"}),
		HairColor:           randomChoice([]string{"black", "brown", "blonde", "red", "gray", "other"}),
		Weight:              randomInt(45, 120),
		SkinTone:            randomChoice([]string{"light", "medium", "dark", "other"}),
		PoliticalLeaning:    randomChoice([]string{"left", "center-left", "center", "center-right", "right", "apolitical"}),
		Region:              randomChoice(regions),
		Device:              randomChoice([]string{"mobile", "desktop", "tablet"}),
		PersonaID:           randomInt(0, 69), // Updated to match the expanded personas list
		SatisfactionScore:   randomFloat(0.3, 0.8),
		EngagementRate:      randomFloat(0.2, 0.6),
		NetworkDensity:      randomFloat(0.1, 0.4),
		InfluenceScore:      randomFloat(0.1, 0.3),
		AvgScrollDepth:      randomFloat(0.3, 0.7),
		AvgWatchTime:        randomFloat(0.2, 0.5),
		ClicksLast24h:       randomInt(0, 10),
		ContentInteractions: randomInt(0, 50),
		VideoCompletionRate: randomFloat(0.3, 0.7),
		Hour:                time.Now().Hour(),
		Preferences:         generatePreferences(),
		CreatedAt:           time.Now(),
	}

	return user
}

// generateUsername generates a random username
func generateUsername() string {
	prefixes := []string{"cool", "awesome", "super", "mega", "ultra", "epic", "pro", "master", "ninja", "guru"}
	suffixes := []string{"user", "gamer", "coder", "dev", "fan", "lover", "hunter", "warrior", "knight", "wizard"}
	
	prefix := randomChoice(prefixes)
	suffix := randomChoice(suffixes)
	number := randomInt(1, 9999)
	
	return prefix + suffix + string(number)
}

// generateEmail generates a random email address
func generateEmail() string {
	domains := []string{"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com"}
	username := generateUsername()
	domain := randomChoice(domains)
	
	return username + "@" + domain
}

// generateAd generates a new ad
func generateAd() Ad {
	ad := Ad{
		ID:            randomString(8),
		Bid:           randomFloat(0.1, 2.0),
		Budget:        randomFloat(100, 1000),
		Category:      randomInt(0, 9),
		Title:         generateAdTitle(),
		Content:       generateAdContent(),
		TargetMetrics: generateTargetMetrics(),
	}

	return ad
}

// generateContentReport generates a new content report
func generateContentReport(user User, contentID string, contentType string) ContentReport {
	report := ContentReport{
		ID:            randomString(8),
		ReporterID:    user.ID,
		ContentID:     contentID,
		ContentType:   contentType,
		ReportReason:  randomChoice([]string{
			ReportReasonSpam,
			ReportReasonHarassment,
			ReportReasonHate,
			ReportReasonViolence,
			ReportReasonCopyright,
			ReportReasonInappropriate,
			ReportReasonOther,
		}),
		ReportDetails:  generateReportDetails(),
		SeverityScore: randomFloat(0.3, 1.0),
		Status:        "pending",
		CreatedAt:     time.Now(),
	}

	return report
}

// generateModerationAction generates a new moderation action
func generateModerationAction(report ContentReport) ModerationAction {
	action := ModerationAction{
		ID:          randomString(8),
		ReportID:    report.ID,
		ModeratorID: randomString(8),
		ActionType:  randomChoice([]string{
			ActionTypeRemove,
			ActionTypeWarn,
			ActionTypeBan,
			ActionTypeFlag,
			ActionTypeIgnore,
		}),
		ActionDetails: generateActionDetails(report),
		CreatedAt:    time.Now(),
	}

	return action
}

// generateContentFlag generates a new content flag
func generateContentFlag(contentID string, contentType string) ContentFlag {
	flag := ContentFlag{
		ID:          randomString(8),
		ContentID:   contentID,
		ContentType: contentType,
		FlagType:    randomChoice([]string{
			FlagTypeTemporary,
			FlagTypePermanent,
			FlagTypeReview,
		}),
		FlagReason:  randomChoice([]string{
			ReportReasonSpam,
			ReportReasonHarassment,
			ReportReasonHate,
			ReportReasonViolence,
			ReportReasonCopyright,
			ReportReasonInappropriate,
		}),
		FlagScore:   randomFloat(0.5, 1.0),
		CreatedAt:   time.Now(),
		ExpiresAt:   time.Now().Add(DefaultFlagDuration),
	}

	return flag
}

// Helper functions for content generation
func generatePreferences() map[string]interface{} {
	preferences := make(map[string]interface{})
	
	// Generate topic preferences
	numTopics := randomInt(1, 5)
	topics := make([]string, numTopics)
	for i := 0; i < numTopics; i++ {
		topics[i] = randomString(10)
	}
	preferences["topics"] = topics
	
	// Generate content type preference
	preferences["content_type"] = randomChoice([]string{"all", "text", "video"})
	
	// Generate category preferences
	numCategories := randomInt(1, 3)
	categories := make([]float64, numCategories)
	for i := 0; i < numCategories; i++ {
		categories[i] = float64(randomInt(0, 9))
	}
	preferences["categories"] = categories
	
	return preferences
}

func generateAdTitle() string {
	titles := []string{
		"Discover Amazing Products",
		"Special Offer Inside",
		"Limited Time Deal",
		"Exclusive Content",
		"Must-See Video",
		"Trending Now",
		"Best Sellers",
		"New Arrivals",
		"Featured Collection",
		"Popular Choice",
	}
	return randomChoice(titles)
}

func generateAdContent() string {
	contents := []string{
		"Check out our latest collection of premium products.",
		"Don't miss out on these incredible deals.",
		"Join thousands of satisfied customers today.",
		"Experience the difference with our exclusive offers.",
		"Transform your life with our innovative solutions.",
		"Get started with our easy-to-use platform.",
		"Find everything you need in one place.",
		"Take advantage of our special promotions.",
		"Upgrade your lifestyle with our premium services.",
		"Discover what everyone is talking about.",
	}
	return randomChoice(contents)
}

func generateTargetMetrics() map[string]float64 {
	metrics := make(map[string]float64)
	
	metrics["min_satisfaction"] = randomFloat(0.3, 0.7)
	metrics["min_engagement"] = randomFloat(0.2, 0.5)
	metrics["min_influence"] = randomFloat(0.1, 0.3)
	
	return metrics
}

func generateReportDetails() string {
	details := []string{
		"This content violates our community guidelines.",
		"The content contains inappropriate material.",
		"This is spam or misleading content.",
		"The content promotes hate or discrimination.",
		"This content infringes on copyright.",
		"The content contains graphic or violent material.",
		"This content is harassing or abusive.",
	}
	return randomChoice(details)
}

func generateActionDetails(report ContentReport) map[string]interface{} {
	details := make(map[string]interface{})
	
	details["reason"] = report.ReportReason
	details["severity"] = report.SeverityScore
	details["action_taken"] = time.Now()
	details["notes"] = "Action taken based on report severity and content type."
	
	return details
} 