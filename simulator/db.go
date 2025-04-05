package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"time"
)

// DB operations for users
func loadUsersFromDB(limit int) ([]User, error) {
	query := `
		SELECT 
			u.id, 
			u.username,
			u.email,
			u.age, 
			u.gender,
			u.eye_color,
			u.hair_color,
			u.weight,
			u.skin_tone,
			u.political_leaning,
			u.region,
			u.device,
			u.persona_id,
			u.satisfaction_score, 
			u.engagement_rate, 
			u.network_density, 
			u.influence_score,
			u.avg_scroll_depth,
			u.avg_watch_time,
			u.clicks_last_24h,
			u.content_interactions,
			u.video_completion_rate,
			u.created_at,
			up.preferences
		FROM users u
		LEFT JOIN user_preferences up ON u.id = up.user_id
		WHERE u.status = 'active'
		ORDER BY RANDOM()
		LIMIT $1
	`

	rows, err := db.Query(query, limit)
	if err != nil {
		return nil, ErrDatabaseQuery("load_users", err)
	}
	defer rows.Close()

	var users []User
	for rows.Next() {
		var user User
		var preferencesJSON []byte
		err := rows.Scan(
			&user.ID,
			&user.Username,
			&user.Email,
			&user.Age,
			&user.Gender,
			&user.EyeColor,
			&user.HairColor,
			&user.Weight,
			&user.SkinTone,
			&user.PoliticalLeaning,
			&user.Region,
			&user.Device,
			&user.PersonaID,
			&user.Satisfaction,
			&user.EngagementRate,
			&user.NetworkDensity,
			&user.InfluenceScore,
			&user.AvgScrollDepth,
			&user.AvgWatchTime,
			&user.ClicksLast24h,
			&user.ContentInteractions,
			&user.VideoCompletionRate,
			&user.CreatedAt,
			&preferencesJSON,
		)
		if err != nil {
			return nil, ErrDatabaseQuery("scan_user", err)
		}

		// Parse preferences JSON
		if len(preferencesJSON) > 0 {
			err = json.Unmarshal(preferencesJSON, &user.Preferences)
			if err != nil {
				LogError("Failed to parse preferences for user %s: %v", user.ID, err)
				user.Preferences = make(map[string]interface{})
			}
		} else {
			user.Preferences = make(map[string]interface{})
		}

		// Set hour for simulation
		user.Hour = time.Now().Hour()

		users = append(users, user)
	}

	if err = rows.Err(); err != nil {
		return nil, ErrDatabaseQuery("iterate_users", err)
	}

	return users, nil
}

// DB operations for ads
func loadAdsFromDB(limit int) ([]Ad, error) {
	query := `
		SELECT 
			a.ad_id, 
			a.bid, 
			a.budget, 
			a.category, 
			a.title, 
			a.content,
			a.target_metrics
		FROM ads a
		WHERE a.budget > 0 AND a.status = 'active'
		ORDER BY RANDOM()
		LIMIT $1
	`

	rows, err := db.Query(query, limit)
	if err != nil {
		return nil, ErrDatabaseQuery("load_ads", err)
	}
	defer rows.Close()

	var ads []Ad
	for rows.Next() {
		var ad Ad
		var targetMetricsJSON []byte
		err := rows.Scan(
			&ad.ID,
			&ad.Bid,
			&ad.Budget,
			&ad.Category,
			&ad.Title,
			&ad.Content,
			&targetMetricsJSON,
		)
		if err != nil {
			return nil, ErrDatabaseQuery("scan_ad", err)
		}

		// Parse target metrics JSON
		if len(targetMetricsJSON) > 0 {
			err = json.Unmarshal(targetMetricsJSON, &ad.TargetMetrics)
			if err != nil {
				LogError("Failed to parse target metrics for ad %s: %v", ad.ID, err)
				ad.TargetMetrics = make(map[string]float64)
			}
		} else {
			ad.TargetMetrics = make(map[string]float64)
		}

		ads = append(ads, ad)
	}

	if err = rows.Err(); err != nil {
		return nil, ErrDatabaseQuery("iterate_ads", err)
	}

	return ads, nil
}

// DB operations for content
func loadContentFromDB(limit int) ([]DBContent, error) {
	query := `
		SELECT 
			p.post_id, 
			p.content_type, 
			p.topic, 
			p.reply_count, 
			p.retweet_count, 
			p.quote_count,
			CASE 
				WHEN p.content_type = 'video' THEN v.completion_rate
				ELSE NULL
			END as completion_rate,
			CASE 
				WHEN p.content_type = 'video' THEN v.watch_time_seconds
				ELSE NULL
			END as watch_time_seconds,
			CASE 
				WHEN p.content_type = 'video' THEN v.loop_count
				ELSE NULL
			END as loop_count,
			p.status,
			p.created_at
		FROM posts p
		LEFT JOIN videos v ON p.post_id = v.post_id
		WHERE p.status = 'active'
		ORDER BY RANDOM()
		LIMIT $1
	`

	rows, err := db.Query(query, limit)
	if err != nil {
		return nil, ErrDatabaseQuery("load_content", err)
	}
	defer rows.Close()

	var contents []DBContent
	for rows.Next() {
		var content DBContent
		err := rows.Scan(
			&content.ID,
			&content.ContentType,
			&content.Topic,
			&content.ReplyCount,
			&content.RetweetCount,
			&content.QuoteCount,
			&content.CompletionRate,
			&content.WatchTime,
			&content.LoopCount,
			&content.Status,
			&content.CreatedAt,
		)
		if err != nil {
			return nil, ErrDatabaseQuery("scan_content", err)
		}

		contents = append(contents, content)
	}

	if err = rows.Err(); err != nil {
		return nil, ErrDatabaseQuery("iterate_content", err)
	}

	return contents, nil
}

// Save simulation results
func saveSimulationResults(result SimulationResult) error {
	tx, err := db.Begin()
	if err != nil {
		return ErrDatabaseQuery("begin_transaction", err)
	}
	defer tx.Rollback()

	// Save ad impressions
	for _, impression := range result.AdImpressions {
		_, err := tx.Exec(`
			INSERT INTO ad_impressions (
				ad_id, user_id, feed_position, feed_type,
				predicted_ctr, actual_click, price_paid, created_at
			)
			VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
		`, impression.AdID, result.UserID, 1, "mixed", 0.1, impression.Clicked, 0.1, impression.Timestamp)
		if err != nil {
			return ErrDatabaseQuery("save_impression", err)
		}
	}

	// Save reports
	for _, report := range result.Reports {
		_, err := tx.Exec(`
			INSERT INTO content_reports (
				reporter_id, content_id, content_type, report_reason, 
				report_details, severity_score, status, created_at
			)
			VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
		`, report.ReporterID, report.ContentID, report.ContentType, report.ReportReason,
			report.ReportDetails, report.SeverityScore, report.Status, report.CreatedAt)
		if err != nil {
			return ErrDatabaseQuery("save_report", err)
		}
	}

	// Save moderation actions
	for _, action := range result.Actions {
		actionDetailsJSON, err := json.Marshal(action.ActionDetails)
		if err != nil {
			return ErrDatabaseQuery("marshal_action_details", err)
		}

		_, err = tx.Exec(`
			INSERT INTO moderation_actions (
				report_id, moderator_id, action_type, action_details, created_at
			)
			VALUES ($1, $2, $3, $4, $5)
		`, action.ReportID, action.ModeratorID, action.ActionType, actionDetailsJSON, action.CreatedAt)
		if err != nil {
			return ErrDatabaseQuery("save_action", err)
		}
	}

	// Save content flags
	for _, flag := range result.Flags {
		_, err := tx.Exec(`
			INSERT INTO content_flags (
				content_id, content_type, flag_type, flag_reason, 
				flag_score, created_at, expires_at
			)
			VALUES ($1, $2, $3, $4, $5, $6, $7)
		`, flag.ContentID, flag.ContentType, flag.FlagType, flag.FlagReason,
			flag.FlagScore, flag.CreatedAt, flag.ExpiresAt)
		if err != nil {
			return ErrDatabaseQuery("save_flag", err)
		}
	}

	// Update user metrics
	_, err = tx.Exec(`
		UPDATE users 
		SET satisfaction_score = $1
		WHERE id = $2
	`, result.Metrics["satisfaction"], result.UserID)
	if err != nil {
		return ErrDatabaseQuery("update_user_metrics", err)
	}

	// Update user network metrics
	_, err = tx.Exec(`
		INSERT INTO user_network_metrics (
			user_id, engagement_rate, network_density, influence_score, last_updated
		)
		VALUES ($1, $2, $3, $4, $5)
		ON CONFLICT (user_id) DO UPDATE SET
			engagement_rate = EXCLUDED.engagement_rate,
			network_density = EXCLUDED.network_density,
			influence_score = EXCLUDED.influence_score,
			last_updated = EXCLUDED.last_updated
	`, result.UserID, result.Metrics["engagement_rate"], result.Metrics["network_density"],
		result.Metrics["influence_score"], time.Now())
	if err != nil {
		return ErrDatabaseQuery("update_network_metrics", err)
	}

	// Commit transaction
	if err = tx.Commit(); err != nil {
		return ErrDatabaseQuery("commit_transaction", err)
	}

	return nil
} 