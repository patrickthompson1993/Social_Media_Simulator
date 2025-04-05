package main

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"time"

	_ "github.com/lib/pq"
)

type CTRRequest struct {
	PersonaID          int     `json:"persona_id"`
	Age               int     `json:"age"`
	Device            int     `json:"device"`
	Hour              int     `json:"hour"`
	AdCategory        int     `json:"ad_category"`
	FeedPosition      int     `json:"feed_position"`
	Match             int     `json:"match"`
	Satisfaction      float64 `json:"satisfaction"`
	EngagementRate    float64 `json:"engagement_rate"`
	NetworkDensity    float64 `json:"network_density"`
	InfluenceScore    float64 `json:"influence_score"`
	DayOfWeek         int     `json:"day_of_week"`
	IsWeekend         int     `json:"is_weekend"`
	AvgScrollDepth    float64 `json:"avg_scroll_depth"`
	AvgWatchTime      float64 `json:"avg_watch_time"`
	ClicksLast24h     int     `json:"clicks_last_24h"`
	ContentInteractions int     `json:"content_interactions"`
	VideoCompletionRate float64 `json:"video_completion_rate"`
}

type CTRResponse struct {
	ClickProbability float64 `json:"click_probability"`
}

type Ad struct {
	ID            string
	Bid           float64
	Budget        float64
	Category      int
	Title         string
	Content       string
	TargetMetrics map[string]float64
}

type User struct {
	ID                  string
	Username            string
	Email               string
	Age                 int
	Gender              string
	EyeColor            string
	HairColor           string
	Weight              int
	SkinTone            string
	PoliticalLeaning    string
	Region              string
	Device              string
	PersonaID           int
	Satisfaction        float64
	EngagementRate      float64
	NetworkDensity      float64
	InfluenceScore      float64
	AvgScrollDepth      float64
	AvgWatchTime        float64
	ClicksLast24h       int
	ContentInteractions int
	VideoCompletionRate float64
	Hour                int
	Preferences         map[string]interface{}
	CreatedAt           time.Time
}

type ContentReport struct {
	ID            string
	ReporterID    string
	ContentID     string
	ContentType   string
	ReportReason  string
	ReportDetails string
	SeverityScore float64
	Status        string
	CreatedAt     time.Time
}

type ModerationAction struct {
	ID           string
	ReportID     string
	ModeratorID  string
	ActionType   string
	ActionDetails map[string]interface{}
	CreatedAt    time.Time
}

type ContentFlag struct {
	ID          string
	ContentID   string
	ContentType string
	FlagType    string
	FlagReason  string
	FlagScore   float64
	CreatedAt   time.Time
	ExpiresAt   time.Time
}

var regions = []string{
	"North America",
	"South America",
	"Europe",
	"Asia",
	"Africa",
	"Oceania",
}

// Database connection
var db *sql.DB

// Initialize database connection
func initDB() error {
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		dbURL = "postgres://postgres:postgres@localhost:5432/socialmedia?sslmode=disable"
	}

	var err error
	db, err = sql.Open("postgres", dbURL)
	if err != nil {
		return fmt.Errorf("error opening database: %v", err)
	}

	// Test the connection
	err = db.Ping()
	if err != nil {
		return fmt.Errorf("error connecting to the database: %v", err)
	}

	log.Println("Successfully connected to database")
	return nil
}

// Load real users from database
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
			unm.engagement_rate,
			unm.network_density,
			unm.influence_score,
			unm.follower_count,
			unm.following_count,
			um.avg_scroll_depth,
			um.avg_watch_time,
			um.clicks_last_24h,
			um.content_interactions,
			um.video_completion_rate,
			u.created_at,
			up.preferences
		FROM users u
		LEFT JOIN user_network_metrics unm ON u.id = unm.user_id
		LEFT JOIN user_metrics um ON u.id = um.user_id
		LEFT JOIN user_preferences up ON u.id = up.user_id
		WHERE u.status = 'active'
		ORDER BY RANDOM()
		LIMIT $1
	`

	rows, err := db.Query(query, limit)
	if err != nil {
		return nil, fmt.Errorf("error querying users: %v", err)
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
			&user.FollowerCount,
			&user.FollowingCount,
			&user.AvgScrollDepth,
			&user.AvgWatchTime,
			&user.ClicksLast24h,
			&user.ContentInteractions,
			&user.VideoCompletionRate,
			&user.CreatedAt,
			&preferencesJSON,
		)
		if err != nil {
			return nil, fmt.Errorf("error scanning user: %v", err)
		}

		// Parse preferences JSON
		if len(preferencesJSON) > 0 {
			err = json.Unmarshal(preferencesJSON, &user.Preferences)
			if err != nil {
				log.Printf("Failed to parse preferences for user %s: %v", user.ID, err)
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
		return nil, fmt.Errorf("error iterating users: %v", err)
	}

	return users, nil
}

// Load real ads from database
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
		WHERE a.budget > 0
		ORDER BY RANDOM()
		LIMIT $1
	`

	rows, err := db.Query(query, limit)
	if err != nil {
		return nil, fmt.Errorf("error querying ads: %v", err)
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
			return nil, fmt.Errorf("error scanning ad: %v", err)
		}

		// Parse target metrics JSON
		if len(targetMetricsJSON) > 0 {
			err = json.Unmarshal(targetMetricsJSON, &ad.TargetMetrics)
			if err != nil {
				log.Printf("Warning: could not parse target metrics for ad %s: %v", ad.ID, err)
				ad.TargetMetrics = make(map[string]float64)
			}
		} else {
			ad.TargetMetrics = make(map[string]float64)
		}

		ads = append(ads, ad)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating ads: %v", err)
	}

	return ads, nil
}

// Save simulation results to database
func saveSimulationResults(user User, selectedAds []Ad, reports []ContentReport, actions []ModerationAction, flags []ContentFlag) error {
	// Start a transaction
	tx, err := db.Begin()
	if err != nil {
		return fmt.Errorf("error beginning transaction: %v", err)
	}
	defer tx.Rollback()

	// Save ad impressions
	for _, ad := range selectedAds {
		_, err := tx.Exec(`
			INSERT INTO ad_impressions (
				ad_id, user_id, feed_position, feed_type,
				predicted_ctr, actual_click, price_paid, created_at
			)
			VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
		`, ad.ID, user.ID, 1, "mixed", 0.1, rand.Float64() < PredictCTR(user, ad, 1), 0.1, time.Now())
		if err != nil {
			return fmt.Errorf("error saving ad impression: %v", err)
		}
	}

	// Save content reports
	for _, report := range reports {
		_, err := tx.Exec(`
			INSERT INTO content_reports (
				reporter_id, content_id, content_type, report_reason, 
				report_details, severity_score, status, created_at
			)
			VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
		`, report.ReporterID, report.ContentID, report.ContentType, report.ReportReason,
			report.ReportDetails, report.SeverityScore, report.Status, report.CreatedAt)
		if err != nil {
			return fmt.Errorf("error saving content report: %v", err)
		}
	}

	// Save moderation actions
	for _, action := range actions {
		actionDetailsJSON, err := json.Marshal(action.ActionDetails)
		if err != nil {
			return fmt.Errorf("error marshaling action details: %v", err)
		}

		_, err = tx.Exec(`
			INSERT INTO moderation_actions (
				report_id, moderator_id, action_type, action_details, created_at
			)
			VALUES ($1, $2, $3, $4, $5)
		`, action.ReportID, action.ModeratorID, action.ActionType, actionDetailsJSON, action.CreatedAt)
		if err != nil {
			return fmt.Errorf("error saving moderation action: %v", err)
		}
	}

	// Save content flags
	for _, flag := range flags {
		_, err := tx.Exec(`
			INSERT INTO content_flags (
				content_id, content_type, flag_type, flag_reason, 
				flag_score, created_at, expires_at
			)
			VALUES ($1, $2, $3, $4, $5, $6, $7)
		`, flag.ContentID, flag.ContentType, flag.FlagType, flag.FlagReason,
			flag.FlagScore, flag.CreatedAt, flag.ExpiresAt)
		if err != nil {
			return fmt.Errorf("error saving content flag: %v", err)
		}
	}

	// Update user metrics
	_, err = tx.Exec(`
		UPDATE users 
		SET 
			satisfaction_score = $1,
			last_active = $2
		WHERE id = $3
	`, user.Satisfaction, time.Now(), user.ID)
	if err != nil {
		return fmt.Errorf("error updating user metrics: %v", err)
	}

	// Update user network metrics
	_, err = tx.Exec(`
		INSERT INTO user_network_metrics (
			user_id, follower_count, following_count,
			engagement_rate, network_density, influence_score,
			last_updated
		)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		ON CONFLICT (user_id) DO UPDATE SET
			follower_count = EXCLUDED.follower_count,
			following_count = EXCLUDED.following_count,
			engagement_rate = EXCLUDED.engagement_rate,
			network_density = EXCLUDED.network_density,
			influence_score = EXCLUDED.influence_score,
			last_updated = EXCLUDED.last_updated
	`, user.ID, user.FollowerCount, user.FollowingCount,
		user.EngagementRate, user.NetworkDensity, user.InfluenceScore,
		time.Now())
	if err != nil {
		return fmt.Errorf("error updating network metrics: %v", err)
	}

	// Update user engagement metrics
	_, err = tx.Exec(`
		INSERT INTO user_metrics (
			user_id, avg_scroll_depth, avg_watch_time,
			clicks_last_24h, content_interactions, video_completion_rate,
			last_updated
		)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		ON CONFLICT (user_id) DO UPDATE SET
			avg_scroll_depth = EXCLUDED.avg_scroll_depth,
			avg_watch_time = EXCLUDED.avg_watch_time,
			clicks_last_24h = EXCLUDED.clicks_last_24h,
			content_interactions = EXCLUDED.content_interactions,
			video_completion_rate = EXCLUDED.video_completion_rate,
			last_updated = EXCLUDED.last_updated
	`, user.ID, user.AvgScrollDepth, user.AvgWatchTime,
		user.ClicksLast24h, user.ContentInteractions, user.VideoCompletionRate,
		time.Now())
	if err != nil {
		return fmt.Errorf("error updating engagement metrics: %v", err)
	}

	// Commit the transaction
	if err = tx.Commit(); err != nil {
		return fmt.Errorf("error committing transaction: %v", err)
	}

	return nil
}

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
		Satisfaction:        randomFloat(0.3, 0.8),
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
	
	return prefix + suffix + strconv.Itoa(number)
}

// generateEmail generates a random email address
func generateEmail() string {
	domains := []string{"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com"}
	username := generateUsername()
	domain := randomChoice(domains)
	
	return username + "@" + domain
}

func generateAd() Ad {
	categories := []string{"tech", "fashion", "gaming", "politics", "memes", "beauty"}
	category := rand.Intn(len(categories))
	return Ad{
		ID:       fmt.Sprintf("ad-%d", rand.Intn(1_000_000)),
		Bid:      rand.Float64()*0.5 + 0.5,
		Budget:   rand.Float64()*200 + 100,
		Category: category,
		Title:    fmt.Sprintf("Ad for %s", categories[category]),
		Content:  "Buy now! Limited time offer!",
		TargetMetrics: map[string]float64{
			"min_satisfaction": rand.Float64() * 0.5,
			"min_engagement":   rand.Float64() * 0.5,
			"min_influence":    rand.Float64() * 5.0,
		},
	}
}

func PredictCTR(user User, ad Ad, feedPosition int) float64 {
	now := time.Now()
	match := 0
	if ad.Category == user.PersonaID || rand.Float64() < 0.3 {
		match = 1
	}

	// Convert device string to integer for CTR prediction
	deviceInt := 0
	switch user.Device {
	case "mobile":
		deviceInt = 0
	case "desktop":
		deviceInt = 1
	case "tablet":
		deviceInt = 2
	default:
		deviceInt = 0 // Default to mobile
	}

	req := CTRRequest{
		PersonaID:          user.PersonaID,
		Age:               user.Age,
		Device:            deviceInt,
		Hour:              user.Hour,
		AdCategory:        ad.Category,
		FeedPosition:      feedPosition,
		Match:             match,
		Satisfaction:      user.Satisfaction,
		EngagementRate:    user.EngagementRate,
		NetworkDensity:    user.NetworkDensity,
		InfluenceScore:    user.InfluenceScore,
		DayOfWeek:         int(now.Weekday()),
		IsWeekend:         boolToInt(now.Weekday() >= 5),
		AvgScrollDepth:    user.AvgScrollDepth,
		AvgWatchTime:      user.AvgWatchTime,
		ClicksLast24h:     user.ClicksLast24h,
		ContentInteractions: user.ContentInteractions,
		VideoCompletionRate: user.VideoCompletionRate,
	}

	jsonReq, _ := json.Marshal(req)
	resp, err := http.Post("http://ctr_model:8001/predict", "application/json", bytes.NewBuffer(jsonReq))
	if err != nil {
		fmt.Println("Prediction error:", err)
		return 0.05
	}
	defer resp.Body.Close()
	var result CTRResponse
	json.NewDecoder(resp.Body).Decode(&result)
	return result.ClickProbability
}

func boolToInt(b bool) int {
	if b {
		return 1
	}
	return 0
}

func meetsTargetMetrics(user User, ad Ad) bool {
	return user.Satisfaction >= ad.TargetMetrics["min_satisfaction"] &&
		user.EngagementRate >= ad.TargetMetrics["min_engagement"] &&
		user.InfluenceScore >= ad.TargetMetrics["min_influence"]
}

func runAuction(user User, ads []Ad, slots int) []Ad {
	type ScoredAd struct {
		Ad
		CTR   float64
		Score float64
	}

	var candidates []ScoredAd
	for _, ad := range ads {
		if ad.Budget < 0.01 || !meetsTargetMetrics(user, ad) {
			continue
		}

		ctr := PredictCTR(user, ad, 1)
		score := ad.Bid * ctr
		
		// Apply quality factors
		score *= (1 + user.Satisfaction * 0.2)
		score *= (1 + user.EngagementRate * 0.15)
		score *= (1 + min(user.InfluenceScore/10, 1.0) * 0.1)

		candidates = append(candidates, ScoredAd{ad, ctr, score})
	}

	selected := []Ad{}
	used := map[string]bool{}

	for len(selected) < slots && len(candidates) > 0 {
		bestIdx := -1
		var best ScoredAd

		for i, c := range candidates {
			if !used[c.ID] && (bestIdx == -1 || c.Score > best.Score) {
				best = c
				bestIdx = i
			}
		}

		if bestIdx == -1 || best.Budget < 0.01 {
			break
		}

		used[best.ID] = true
		best.Budget -= best.Bid * 0.8
		selected = append(selected, best.Ad)

		candidates = append(candidates[:bestIdx], candidates[bestIdx+1:]...)
	}

	return selected
}

func generateContentReport(user User, contentID string, contentType string) ContentReport {
	reportReasons := []string{
		"spam", "hate_speech", "violence", "harassment", "misinformation",
		"inappropriate", "copyright", "other",
	}
	
	return ContentReport{
		ID:            fmt.Sprintf("report-%d", rand.Intn(1_000_000)),
		ReporterID:    user.ID,
		ContentID:     contentID,
		ContentType:   contentType,
		ReportReason:  reportReasons[rand.Intn(len(reportReasons))],
		ReportDetails: "User reported content for violation",
		SeverityScore: rand.Float64(),
		Status:        "pending",
		CreatedAt:     time.Now(),
	}
}

func generateModerationAction(report ContentReport) ModerationAction {
	actionTypes := []string{
		"warn", "remove_content", "ban_user", "restrict_user",
		"flag_content", "dismiss_report",
	}
	
	return ModerationAction{
		ID:           fmt.Sprintf("action-%d", rand.Intn(1_000_000)),
		ReportID:     report.ID,
		ModeratorID:  fmt.Sprintf("mod-%d", rand.Intn(1_000_000)),
		ActionType:   actionTypes[rand.Intn(len(actionTypes))],
		ActionDetails: map[string]interface{}{
			"reason": "Content violates community guidelines",
			"duration": rand.Intn(30) + 1,
		},
		CreatedAt:    time.Now(),
	}
}

func generateContentFlag(contentID string, contentType string) ContentFlag {
	flagTypes := []string{
		"auto_moderated", "user_reported", "admin_flagged", "ai_flagged",
	}
	
	return ContentFlag{
		ID:          fmt.Sprintf("flag-%d", rand.Intn(1_000_000)),
		ContentID:   contentID,
		ContentType: contentType,
		FlagType:    flagTypes[rand.Intn(len(flagTypes))],
		FlagReason:  "Content flagged for review",
		FlagScore:   rand.Float64(),
		CreatedAt:   time.Now(),
		ExpiresAt:   time.Now().Add(time.Hour * 24 * time.Duration(rand.Intn(30)+1)),
	}
}

func shouldReportContent(user User, ad Ad) bool {
	// Simulate content reporting based on user characteristics
	baseProb := 0.01 // Base 1% chance of reporting
	
	// Increase probability based on user characteristics
	if user.Satisfaction < 0.3 {
		baseProb += 0.05
	}
	if user.EngagementRate < 0.2 {
		baseProb += 0.03
	}
	
	// Decrease probability for satisfied users
	if user.Satisfaction > 0.8 {
		baseProb -= 0.02
	}
	
	return rand.Float64() < baseProb
}

// Simulate content feed interaction
func SimulateFeedInteraction(user User) error {
	// Load content from database
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
			p.created_at
		FROM posts p
		LEFT JOIN videos v ON p.post_id = v.post_id
		WHERE p.created_at > NOW() - INTERVAL '7 days'
		ORDER BY RANDOM()
		LIMIT 10
	`

	rows, err := db.Query(query)
	if err != nil {
		return fmt.Errorf("error querying content: %v", err)
	}
	defer rows.Close()

	var contents []struct {
		PostID           string
		ContentType      string
		Topic            string
		ReplyCount       int
		RetweetCount     int
		QuoteCount       int
		CompletionRate   sql.NullFloat64
		WatchTimeSeconds sql.NullInt64
		LoopCount        sql.NullInt64
		CreatedAt        time.Time
	}

	for rows.Next() {
		var content struct {
			PostID           string
			ContentType      string
			Topic            string
			ReplyCount       int
			RetweetCount     int
			QuoteCount       int
			CompletionRate   sql.NullFloat64
			WatchTimeSeconds sql.NullInt64
			LoopCount        sql.NullInt64
			CreatedAt        time.Time
		}

		err := rows.Scan(
			&content.PostID,
			&content.ContentType,
			&content.Topic,
			&content.ReplyCount,
			&content.RetweetCount,
			&content.QuoteCount,
			&content.CompletionRate,
			&content.WatchTimeSeconds,
			&content.LoopCount,
			&content.CreatedAt,
		)
		if err != nil {
			return fmt.Errorf("error scanning content: %v", err)
		}

		contents = append(contents, content)
	}

	if err = rows.Err(); err != nil {
		return fmt.Errorf("error iterating content: %v", err)
	}

	// Simulate user interaction with content
	for _, content := range contents {
		// Determine if user interacts with content based on preferences and content type
		interactionProb := 0.3 // Base probability

		// Adjust based on user preferences
		if preferences, ok := user.Preferences["topics"].([]interface{}); ok {
			for _, topic := range preferences {
				if topicStr, ok := topic.(string); ok && topicStr == content.Topic {
					interactionProb += 0.2
					break
				}
			}
		}

		// Adjust based on content type preference
		if contentType, ok := user.Preferences["content_type"].(string); ok {
			if contentType == "all" || contentType == content.ContentType {
				interactionProb += 0.1
			}
		}

		// Adjust based on user engagement rate
		interactionProb += user.EngagementRate * 0.2

		// Determine if user interacts
		if rand.Float64() < interactionProb {
			// Determine interaction type
			interactionTypes := []string{"view", "like", "share", "comment", "bookmark", "retweet", "quote"}
			interactionWeights := []float64{0.5, 0.2, 0.1, 0.1, 0.05, 0.03, 0.02}
			
			interactionType := interactionTypes[weightedRandomChoice(interactionWeights)]
			
			// Save interaction to database
			_, err := db.Exec(`
				INSERT INTO content_interactions (
					user_id, post_id, interaction_type, timestamp
				)
				VALUES ($1, $2, $3, $4)
			`, user.ID, content.PostID, interactionType, time.Now())
			if err != nil {
				return fmt.Errorf("error saving content interaction: %v", err)
			}
			
			// Update user metrics
			user.ContentInteractions++
			
			// Update video completion rate if applicable
			if content.ContentType == "video" && content.CompletionRate.Valid {
				user.VideoCompletionRate = (user.VideoCompletionRate*float64(user.ContentInteractions) + content.CompletionRate.Float64) / float64(user.ContentInteractions+1)
			}
			
			// Check if user should report content
			if shouldReportContent(user, ad) {
				report := generateContentReport(user, content.PostID, content.ContentType)
				
				// Save report to database
				_, err := db.Exec(`
					INSERT INTO content_reports (
						reporter_id, content_id, content_type, report_reason, 
						report_details, severity_score, status, created_at
					)
					VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
				`, report.ReporterID, report.ContentID, report.ContentType, report.ReportReason,
					report.ReportDetails, report.SeverityScore, report.Status, report.CreatedAt)
				if err != nil {
					return fmt.Errorf("error saving content report: %v", err)
				}
				
				// Generate and save moderation action
				action := generateModerationAction(report)
				log.Printf("[Moderation] Action taken on report %s: %s\n", report.ID, action.ActionType)
				actions = append(actions, action)
				
				// Generate and save content flag
				flag := generateContentFlag(content.PostID, content.ContentType)
				log.Printf("[Flag] Content %s flagged as %s\n", content.PostID, flag.FlagType)
				flags = append(flags, flag)
			}
		}
	}

	return nil
}

// Helper function for weighted random choice
func weightedRandomChoice(weights []float64) int {
	sum := 0.0
	for _, w := range weights {
		sum += w
	}
	
	r := rand.Float64() * sum
	
	for i, w := range weights {
		r -= w
		if r <= 0 {
			return i
		}
	}
	
	return len(weights) - 1
}

// Simulate user network growth
func SimulateNetworkGrowth(user User) error {
	// Load potential connections from database
	query := `
		SELECT 
			u.id,
			unm.follower_count,
			unm.following_count,
			unm.network_density,
			unm.influence_score
		FROM users u
		LEFT JOIN user_network_metrics unm ON u.id = unm.user_id
		WHERE u.id != $1
			AND NOT EXISTS (
				SELECT 1 FROM user_relationships ur
				WHERE ur.follower_id = $1
				AND ur.following_id = u.id
				AND ur.relationship_type = 'follow'
			)
		ORDER BY RANDOM()
		LIMIT 20
	`

	rows, err := db.Query(query, user.ID)
	if err != nil {
		return fmt.Errorf("error querying potential connections: %v", err)
	}
	defer rows.Close()

	var potentialConnections []struct {
		UserID        string
		FollowerCount int
		FollowingCount int
		NetworkDensity float64
		InfluenceScore float64
	}

	for rows.Next() {
		var connection struct {
			UserID        string
			FollowerCount int
			FollowingCount int
			NetworkDensity float64
			InfluenceScore float64
		}

		err := rows.Scan(
			&connection.UserID,
			&connection.FollowerCount,
			&connection.FollowingCount,
			&connection.NetworkDensity,
			&connection.InfluenceScore,
		)
		if err != nil {
			return fmt.Errorf("error scanning potential connection: %v", err)
		}

		potentialConnections = append(potentialConnections, connection)
	}

	if err = rows.Err(); err != nil {
		return fmt.Errorf("error iterating potential connections: %v", err)
	}

	// Start a transaction for network updates
	tx, err := db.Begin()
	if err != nil {
		return fmt.Errorf("error beginning transaction: %v", err)
	}
	defer tx.Rollback()

	// Simulate connection formation
	for _, connection := range potentialConnections {
		// Calculate connection probability based on network metrics
		connectionProb := 0.1 // Base probability

		// Adjust based on network density and influence
		connectionProb += connection.NetworkDensity * 0.2
		connectionProb += min(connection.InfluenceScore/10, 1.0) * 0.1

		// Increase probability for users with similar follower/following ratios
		if connection.FollowerCount > 0 && connection.FollowingCount > 0 {
			userRatio := float64(user.FollowerCount) / float64(user.FollowingCount)
			connRatio := float64(connection.FollowerCount) / float64(connection.FollowingCount)
			if abs(userRatio-connRatio) < 0.5 {
				connectionProb += 0.1
			}
		}

		// Determine if connection is formed
		if rand.Float64() < connectionProb {
			// Create follow relationship
			_, err := tx.Exec(`
				INSERT INTO user_relationships (
					follower_id, following_id, relationship_type, created_at
				)
				VALUES ($1, $2, $3, $4)
				ON CONFLICT (follower_id, following_id, relationship_type) DO NOTHING
			`, user.ID, connection.UserID, "follow", time.Now())
			if err != nil {
				return fmt.Errorf("error creating relationship: %v", err)
			}

			// Update follower's network metrics
			_, err = tx.Exec(`
				INSERT INTO user_network_metrics (
					user_id, follower_count, following_count, 
					engagement_rate, network_density, influence_score,
					last_updated
				)
				VALUES ($1, 0, 1, $2, $3, $4, $5)
				ON CONFLICT (user_id) DO UPDATE SET
					following_count = user_network_metrics.following_count + 1,
					network_density = LEAST(1.0, user_network_metrics.network_density + 0.01),
					last_updated = EXCLUDED.last_updated
			`, user.ID, user.EngagementRate, user.NetworkDensity, user.InfluenceScore, time.Now())
			if err != nil {
				return fmt.Errorf("error updating follower metrics: %v", err)
			}

			// Update followed user's network metrics
			_, err = tx.Exec(`
				INSERT INTO user_network_metrics (
					user_id, follower_count, following_count,
					engagement_rate, network_density, influence_score,
					last_updated
				)
				VALUES ($1, 1, 0, $2, $3, $4, $5)
				ON CONFLICT (user_id) DO UPDATE SET
					follower_count = user_network_metrics.follower_count + 1,
					influence_score = LEAST(10.0, user_network_metrics.influence_score + 0.1),
					last_updated = EXCLUDED.last_updated
			`, connection.UserID, connection.NetworkDensity, connection.NetworkDensity, connection.InfluenceScore, time.Now())
			if err != nil {
				return fmt.Errorf("error updating followed user metrics: %v", err)
			}
		}
	}

	// Commit all network updates
	if err = tx.Commit(); err != nil {
		return fmt.Errorf("error committing network updates: %v", err)
	}

	return nil
}

// Simulate user churn
func SimulateUserChurn(user User) bool {
	// Calculate churn probability
	churnProb := 0.01 // Base probability
	
	// Adjust based on satisfaction
	churnProb += (1.0 - user.Satisfaction) * 0.5
	
	// Determine if user churns
	if rand.Float64() < churnProb {
		// Record churn event in database
		_, err := db.Exec(`
			INSERT INTO churn_events (
				user_id, reason, satisfaction_score, created_at
			)
			VALUES ($1, $2, $3, $4)
		`, user.ID, "low_satisfaction", user.Satisfaction, time.Now())
		if err != nil {
			log.Printf("Error recording churn event: %v", err)
		}
		
		return true
	}
	
	return false
}

// SimulateStep with database integration
func SimulateStep() error {
	// Load real users from database
	users, err := loadUsersFromDB(5)
	if err != nil {
		log.Printf("Error loading users: %v", err)
		// Fall back to generating a user
		user := generateUser()
		users = []User{user}
	}
	
	// Load real ads from database
	ads, err := loadAdsFromDB(10)
	if err != nil {
		log.Printf("Error loading ads: %v", err)
		// Fall back to generating ads
		ads = []Ad{
			generateAd(),
			generateAd(),
			generateAd(),
		}
	}
	
	// Process each user
	for _, user := range users {
		// Run ad auction
		selected := runAuction(user, ads, 3)
		
		if len(selected) == 0 {
			log.Printf("[No Ads] for user %s\n", user.ID)
			continue
		}
		
		// Track reports, actions, and flags
		var reports []ContentReport
		var actions []ModerationAction
		var flags []ContentFlag
		
		// Process selected ads
		for _, ad := range selected {
			log.Printf("[Impression] User %s saw Ad %s in category %d\n", user.ID, ad.ID, ad.Category)
			
			// Check for content reporting
			if shouldReportContent(user, ad) {
				report := generateContentReport(user, ad.ID, "ad")
				log.Printf("[Report] User %s reported Ad %s for %s\n", user.ID, ad.ID, report.ReportReason)
				reports = append(reports, report)
				
				// Simulate moderation action
				action := generateModerationAction(report)
				log.Printf("[Moderation] Action taken on report %s: %s\n", report.ID, action.ActionType)
				actions = append(actions, action)
				
				// Add content flag
				flag := generateContentFlag(ad.ID, "ad")
				log.Printf("[Flag] Content %s flagged as %s\n", ad.ID, flag.FlagType)
				flags = append(flags, flag)
			}
			
			// Update user metrics based on ad interaction
			if rand.Float64() < 0.1 {
				user.Satisfaction += 0.02
				user.EngagementRate += 0.01
				user.ClicksLast24h++
			} else {
				user.Satisfaction -= 0.01
			}
			
			// Update content interactions
			user.ContentInteractions++
			if rand.Float64() < 0.3 {
				user.VideoCompletionRate = (user.VideoCompletionRate*float64(user.ContentInteractions) + rand.Float64()) / float64(user.ContentInteractions+1)
			}
		}
		
		// Simulate feed interaction
		err := SimulateFeedInteraction(user)
		if err != nil {
			log.Printf("Error simulating feed interaction: %v", err)
		}
		
		// Simulate network growth
		err = SimulateNetworkGrowth(user)
		if err != nil {
			log.Printf("Error simulating network growth: %v", err)
		}
		
		// Check for user churn
		if SimulateUserChurn(user) {
			log.Printf("[CHURN] User %s left with satisfaction %.2f\n", user.ID, user.Satisfaction)
			continue
		}
		
		// Save simulation results to database
		err = saveSimulationResults(user, selected, reports, actions, flags)
		if err != nil {
			log.Printf("Error saving simulation results: %v", err)
		}
	}
	
	return nil
}

// Helper functions for random generation
func randomString(length int) string {
	const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	result := make([]byte, length)
	for i := range result {
		result[i] = charset[rand.Intn(len(charset))]
	}
	return string(result)
}

func randomInt(min, max int) int {
	return min + rand.Intn(max-min+1)
}

func randomFloat(min, max float64) float64 {
	return min + rand.Float64()*(max-min)
}

func randomChoice(choices []string) string {
	return choices[rand.Intn(len(choices))]
}

func generatePreferences() map[string]interface{} {
	topics := []string{"tech", "fashion", "gaming", "sports", "politics", "entertainment", "science", "health", "business", "education"}
	contentTypes := []string{"all", "videos", "text", "images", "audio"}
	
	// Select 2-4 random topics
	numTopics := randomInt(2, 4)
	selectedTopics := make([]string, numTopics)
	for i := 0; i < numTopics; i++ {
		selectedTopics[i] = randomChoice(topics)
	}
	
	return map[string]interface{}{
		"topics":        selectedTopics,
		"content_type":  randomChoice(contentTypes),
		"language":      randomChoice([]string{"en", "es", "fr", "de", "it", "pt", "ru", "ja", "zh", "ar"}),
		"notifications": randomChoice([]string{"all", "important", "none"}),
	}
}
