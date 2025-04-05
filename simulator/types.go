package main

import (
	"time"
)

// User represents a user in the simulation
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
	SatisfactionScore   float64
	EngagementRate      float64
	NetworkDensity      float64
	InfluenceScore      float64
	AvgScrollDepth      float64
	AvgWatchTime        float64
	ClicksLast24h       int
	ContentInteractions int
	VideoCompletionRate float64
	FollowerCount       int
	FollowingCount      int
	Hour                int
	Preferences         map[string]interface{}
	CreatedAt           time.Time
}

// Ad represents an advertisement
type Ad struct {
	ID            string
	Bid           float64
	Budget        float64
	Category      int
	Title         string
	Content       string
	TargetMetrics map[string]float64
}

// ContentReport represents a report of content
type ContentReport struct {
	ID             string
	ReporterID     string
	ContentID      string
	ContentType    string
	ReportReason   string
	ReportDetails  string
	SeverityScore  float64
	Status         string
	CreatedAt      time.Time
}

// ModerationAction represents an action taken by a moderator
type ModerationAction struct {
	ID            string
	ReportID      string
	ModeratorID   string
	ActionType    string
	ActionDetails map[string]interface{}
	CreatedAt     time.Time
}

// ContentFlag represents a flag on content
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

// CTRRequest represents a request to predict CTR
type CTRRequest struct {
	UserID            string                 `json:"user_id"`
	AdID              string                 `json:"ad_id"`
	UserMetrics       map[string]float64     `json:"user_metrics"`
	AdMetrics         map[string]float64     `json:"ad_metrics"`
	Context           map[string]interface{} `json:"context"`
}

// CTRResponse represents a CTR prediction response
type CTRResponse struct {
	CTR     float64 `json:"ctr"`
	Score   float64 `json:"score"`
	Quality float64 `json:"quality"`
}

// ContentRequest represents a request to predict content interaction
type ContentRequest struct {
	UserID            string                 `json:"user_id"`
	ContentID         string                 `json:"content_id"`
	ContentType       string                 `json:"content_type"`
	UserMetrics       map[string]float64     `json:"user_metrics"`
	ContentMetrics    map[string]float64     `json:"content_metrics"`
	Context           map[string]interface{} `json:"context"`
}

// ContentResponse represents a content interaction prediction response
type ContentResponse struct {
	InteractionProb float64 `json:"interaction_prob"`
	CompletionProb  float64 `json:"completion_prob"`
	EngagementScore float64 `json:"engagement_score"`
}

// FeedRequest represents a request to predict feed engagement
type FeedRequest struct {
	UserID            string                 `json:"user_id"`
	UserMetrics       map[string]float64     `json:"user_metrics"`
	FeedMetrics       map[string]float64     `json:"feed_metrics"`
	Context           map[string]interface{} `json:"context"`
}

// FeedResponse represents a feed engagement prediction response
type FeedResponse struct {
	EngagementProb float64 `json:"engagement_prob"`
	ScrollDepth    float64 `json:"scroll_depth"`
	TimeSpent      float64 `json:"time_spent"`
}

// SimulationResult represents the result of a simulation step
type SimulationResult struct {
	UserID      string
	AdImpressions []AdImpression
	Reports      []ContentReport
	Actions      []ModerationAction
	Flags        []ContentFlag
	Metrics      map[string]float64
	Timestamp    time.Time
}

// AdImpression represents an ad impression
type AdImpression struct {
	AdID       string
	Clicked    bool
	Timestamp  time.Time
}

// Database models
type DBUser struct {
	ID                  string    `db:"user_id"`
	Age                 int       `db:"age"`
	Satisfaction        float64   `db:"satisfaction_score"`
	EngagementRate      float64   `db:"engagement_rate"`
	NetworkDensity      float64   `db:"network_density"`
	InfluenceScore      float64   `db:"influence_score"`
	AvgScrollDepth      float64   `db:"avg_scroll_depth"`
	AvgWatchTime        float64   `db:"avg_watch_time"`
	ClicksLast24h       int       `db:"clicks_last_24h"`
	ContentInteractions int       `db:"content_interactions"`
	VideoCompletionRate float64   `db:"video_completion_rate"`
	Status              string    `db:"status"`
	LastActive          time.Time `db:"last_active"`
	CreatedAt           time.Time `db:"created_at"`
}

type DBAd struct {
	ID            string    `db:"ad_id"`
	Bid           float64   `db:"bid"`
	Budget        float64   `db:"budget"`
	Category      int       `db:"category"`
	Title         string    `db:"title"`
	Content       string    `db:"content"`
	TargetMetrics string    `db:"target_metrics"`
	Status        string    `db:"status"`
	CreatedAt     time.Time `db:"created_at"`
}

type DBContent struct {
	ID             string    `db:"content_id"`
	ContentType    string    `db:"content_type"`
	Topic          string    `db:"topic"`
	ReplyCount     int       `db:"reply_count"`
	RetweetCount   int       `db:"retweet_count"`
	QuoteCount     int       `db:"quote_count"`
	CompletionRate float64   `db:"completion_rate"`
	WatchTime      int       `db:"watch_time_seconds"`
	LoopCount      int       `db:"loop_count"`
	Status         string    `db:"status"`
	CreatedAt      time.Time `db:"created_at"`
}

// UserNetworkMetrics represents network metrics for a user
type UserNetworkMetrics struct {
	UserID              string
	FollowerCount       int
	FollowingCount      int
	EngagementRate      float64
	NetworkDensity      float64
	InfluenceScore      float64
	CommunityClusters   map[string]interface{}
	LastUpdated         time.Time
}

// UserMetrics represents detailed user metrics
type UserMetrics struct {
	UserID              string
	AvgScrollDepth      float64
	AvgWatchTime        float64
	ClicksLast24h       int
	ContentInteractions int
	VideoCompletionRate float64
	LastUpdated         time.Time
} 