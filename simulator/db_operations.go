package main

import (
    "database/sql"
    "encoding/json"
    "math/rand"
    "time"
)

// Additional database operations to align with schema

func trackUserSession(user User, duration int) error {
    query := `
        INSERT INTO user_sessions (
            user_id, session_length_seconds, avg_scroll_depth,
            avg_watch_time, feed_type, clicks
        ) VALUES ($1, $2, $3, $4, $5, $6)
    `
    
    _, err := db.Exec(query,
        user.ID,
        duration,
        user.AvgScrollDepth,
        user.AvgWatchTime,
        "mixed", // or specific feed type
        user.ClicksLast24h,
    )
    
    return err
}

func trackContentRecommendation(user User, contentID string, score float64) error {
    reasonJSON, err := json.Marshal(map[string]interface{}{
        "user_interests": user.Preferences["topics"],
        "engagement_history": user.ContentInteractions,
    })
    if err != nil {
        return err
    }

    query := `
        INSERT INTO content_recommendations (
            user_id, post_id, feed_type, recommendation_source,
            recommendation_score, recommendation_reason
        ) VALUES ($1, $2, $3, $4, $5, $6)
    `
    
    _, err = db.Exec(query,
        user.ID,
        contentID,
        "mixed",
        "algorithm",
        score,
        reasonJSON,
    )
    
    return err
}

func trackUserFeedback(user User, feedbackType string, content string) error {
    query := `
        INSERT INTO user_feedback (
            user_id, feedback_type, feedback_content,
            sentiment_score, priority_score, status
        ) VALUES ($1, $2, $3, $4, $5, $6)
    `
    
    sentimentScore := randomFloat(0.0, 1.0)
    priorityScore := randomFloat(0.0, 1.0)
    
    _, err := db.Exec(query,
        user.ID,
        feedbackType,
        content,
        sentimentScore,
        priorityScore,
        "new",
    )
    
    return err
}

func updateUserPreferences(user User) error {
    // Extract preferences from the user struct
    notificationSettings := map[string]interface{}{
        "email": randomChoice([]string{"all", "important", "none"}),
        "push": randomChoice([]string{"all", "important", "none"}),
        "in_app": randomChoice([]string{"all", "important", "none"}),
    }
    
    privacySettings := map[string]interface{}{
        "profile_visibility": randomChoice([]string{"public", "friends", "private"}),
        "activity_visibility": randomChoice([]string{"public", "friends", "private"}),
        "location_sharing": randomChoice([]string{"on", "off"}),
    }
    
    contentPreferences := map[string]interface{}{
        "topics": user.Preferences["topics"],
        "content_type": user.Preferences["content_type"],
        "language": user.Preferences["language"],
    }
    
    // Marshal the preference objects
    notificationJSON, err := json.Marshal(notificationSettings)
    if err != nil {
        return err
    }
    
    privacyJSON, err := json.Marshal(privacySettings)
    if err != nil {
        return err
    }
    
    contentJSON, err := json.Marshal(contentPreferences)
    if err != nil {
        return err
    }

    query := `
        INSERT INTO user_preferences (
            user_id, notification_settings, privacy_settings,
            content_preferences, language_preference, theme_preference,
            timezone, last_updated
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (user_id) DO UPDATE SET
            notification_settings = EXCLUDED.notification_settings,
            privacy_settings = EXCLUDED.privacy_settings,
            content_preferences = EXCLUDED.content_preferences,
            language_preference = EXCLUDED.language_preference,
            theme_preference = EXCLUDED.theme_preference,
            timezone = EXCLUDED.timezone,
            last_updated = EXCLUDED.last_updated
    `
    
    _, err = db.Exec(query,
        user.ID,
        notificationJSON,
        privacyJSON,
        contentJSON,
        user.Preferences["language"],
        randomChoice([]string{"light", "dark", "system"}),
        randomChoice([]string{"UTC", "EST", "PST", "GMT", "CET", "IST"}),
        time.Now(),
    )
    
    return err
}

func updateUserNetworkMetrics(user User) error {
    query := `
        INSERT INTO user_network_metrics (
            user_id, follower_count, following_count,
            engagement_rate, network_density, influence_score,
            community_clusters, last_updated
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (user_id) DO UPDATE SET
            follower_count = EXCLUDED.follower_count,
            following_count = EXCLUDED.following_count,
            engagement_rate = EXCLUDED.engagement_rate,
            network_density = EXCLUDED.network_density,
            influence_score = EXCLUDED.influence_score,
            community_clusters = EXCLUDED.community_clusters,
            last_updated = EXCLUDED.last_updated
    `
    
    clustersJSON, err := json.Marshal(map[string]interface{}{
        "primary": randomInt(1, 5),
        "secondary": randomInt(1, 3),
    })
    if err != nil {
        return err
    }
    
    _, err = db.Exec(query,
        user.ID,
        int(user.NetworkDensity * 100), // approximate follower count
        int(user.NetworkDensity * 80),  // approximate following count
        user.EngagementRate,
        user.NetworkDensity,
        user.InfluenceScore,
        clustersJSON,
        time.Now(),
    )
    
    return err
}

// Helper function for random choice
func randomChoice(choices []string) string {
	return choices[rand.Intn(len(choices))]
} 