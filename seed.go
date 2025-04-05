package main

import (
    "database/sql"
    "encoding/json"
    "fmt"
    "math/rand"
    "time"

    _ "github.com/lib/pq"
)

const dbURL = "postgres://postgres:postgres@localhost:5432/socialmedia?sslmode=disable"

func randomChoice(list []string) string {
    return list[rand.Intn(len(list))]
}

func insertUser(db *sql.DB) string {
    id := fmt.Sprintf("user-%d", rand.Intn(1_000_000))
    satisfaction := rand.Float64()*0.6 + 0.4
    region := randomChoice([]string{"US", "UK", "IN", "BR", "DE", "FR", "JP", "AU", "CA", "SG"})
    device := randomChoice([]string{"mobile", "desktop", "tablet"})
    personaID := rand.Intn(20)
    
    _, err := db.Exec(`
        INSERT INTO users (
            id, username, email, age, gender, region, device, persona_id,
            satisfaction_score, created_at, last_active, status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
    `, id, id, id+"@example.com", rand.Intn(60)+12,
        randomChoice([]string{"male", "female", "other"}),
        region, device, personaID, satisfaction,
        time.Now().Add(-time.Duration(rand.Intn(30))*24*time.Hour),
        time.Now().Add(-time.Duration(rand.Intn(24))*time.Hour),
        randomChoice([]string{"active", "inactive", "suspended"}))

    if err != nil {
        fmt.Println("Insert user failed:", err)
    }
    return id
}

func insertContent(db *sql.DB, userID string) string {
    id := fmt.Sprintf("content-%d", rand.Intn(1_000_000))
    contentType := randomChoice([]string{"post", "comment", "thread", "video"})
    topic := randomChoice([]string{"tech", "fashion", "gaming", "politics", "memes", "beauty"})
    isVideo := contentType == "video"
    
    _, err := db.Exec(`
        INSERT INTO content (
            id, user_id, content_type, topic, content, is_video,
            created_at, updated_at, status, engagement_score
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    `, id, userID, contentType, topic, "Generated content "+id, isVideo,
        time.Now().Add(-time.Duration(rand.Intn(30))*24*time.Hour),
        time.Now().Add(-time.Duration(rand.Intn(24))*time.Hour),
        randomChoice([]string{"active", "flagged", "removed"}),
        rand.Float64())

    if err != nil {
        fmt.Println("Insert content failed:", err)
    }

    if isVideo {
        _, err := db.Exec(`
            INSERT INTO videos (
                content_id, duration_seconds, resolution, thumbnail_url,
                completion_rate, watch_time_seconds
            )
            VALUES ($1, $2, $3, $4, $5, $6)
        `, id, rand.Intn(300)+30, "1080p", "https://placekitten.com/300/200",
            rand.Float64(), rand.Float64()*300)
        if err != nil {
            fmt.Println("Insert video failed:", err)
        }
    }

    return id
}

func insertAd(db *sql.DB) string {
    id := fmt.Sprintf("ad-%d", rand.Intn(1_000_000))
    advertiserID := fmt.Sprintf("advertiser-%d", rand.Intn(1_000_000))
    contentType := randomChoice([]string{"post", "video", "thread"})
    
    _, err := db.Exec(`
        INSERT INTO ads (
            id, advertiser_id, title, content, content_type,
            budget, ctr, conversion_rate, status, created_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    `, id, advertiserID, "Ad for "+id, "Buy now!", contentType,
        100+rand.Float64()*400, rand.Float64()*0.3,
        rand.Float64()*0.1, randomChoice([]string{"active", "paused", "completed"}),
        time.Now().Add(-time.Duration(rand.Intn(30))*24*time.Hour))
    
    if err != nil {
        fmt.Println("Insert ad failed:", err)
    }
    return id
}

func insertEngagement(db *sql.DB, userID, contentID string) {
    engagementType := randomChoice([]string{"like", "comment", "share", "bookmark"})
    _, err := db.Exec(`
        INSERT INTO engagements (
            user_id, content_id, engagement_type, created_at
        )
        VALUES ($1, $2, $3, $4)
    `, userID, contentID, engagementType, time.Now())
    
    if err != nil {
        fmt.Println("Engagement failed:", err)
    }
}

func insertAdImpression(db *sql.DB, userID, adID string) {
    predictedCTR := rand.Float64()*0.3 + 0.1
    actualClick := rand.Float64() < predictedCTR
    price := rand.Float64() * 3

    _, err := db.Exec(`
        INSERT INTO ad_impressions (
            ad_id, user_id, feed_position, predicted_ctr,
            actual_click, price_paid, created_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
    `, adID, userID, rand.Intn(5)+1, predictedCTR,
        actualClick, price, time.Now())
    
    if err != nil {
        fmt.Println("Impression failed:", err)
    }
}

func insertModerationReport(db *sql.DB, userID, contentID string) {
    reportReason := randomChoice([]string{
        "spam", "hate_speech", "violence", "harassment",
        "misinformation", "inappropriate", "copyright", "other"
    })
    
    _, err := db.Exec(`
        INSERT INTO moderation_reports (
            reporter_id, content_id, report_reason,
            severity_score, status, created_at
        )
        VALUES ($1, $2, $3, $4, $5, $6)
    `, userID, contentID, reportReason,
        rand.Float64(), randomChoice([]string{"pending", "resolved", "dismissed"}),
        time.Now())
    
    if err != nil {
        fmt.Println("Moderation report failed:", err)
    }
}

func insertModerationAction(db *sql.DB, reportID string) {
    moderatorID := fmt.Sprintf("moderator-%d", rand.Intn(1_000_000))
    actionType := randomChoice([]string{
        "warn", "remove_content", "ban_user", "restrict_user",
        "flag_content", "dismiss_report"
    })
    
    _, err := db.Exec(`
        INSERT INTO moderation_actions (
            report_id, moderator_id, action_type,
            created_at
        )
        VALUES ($1, $2, $3, $4)
    `, reportID, moderatorID, actionType, time.Now())
    
    if err != nil {
        fmt.Println("Moderation action failed:", err)
    }
}

func insertUserSatisfaction(db *sql.DB, userID string) {
    satisfactionLevel := randomChoice([]string{"high", "medium", "low"})
    _, err := db.Exec(`
        INSERT INTO user_satisfaction (
            user_id, satisfaction_level, created_at
        )
        VALUES ($1, $2, $3)
    `, userID, satisfactionLevel, time.Now())
    
    if err != nil {
        fmt.Println("User satisfaction failed:", err)
    }
}

func insertModelPrediction(db *sql.DB, userID, contentID string) {
    predictionType := randomChoice([]string{"ctr", "engagement", "satisfaction"})
    confidence := rand.Float64()*0.3 + 0.7
    
    _, err := db.Exec(`
        INSERT INTO model_predictions (
            user_id, content_id, prediction_type,
            predicted_value, confidence, created_at
        )
        VALUES ($1, $2, $3, $4, $5, $6)
    `, userID, contentID, predictionType,
        rand.Float64(), confidence, time.Now())
    
    if err != nil {
        fmt.Println("Model prediction failed:", err)
    }
}

func insertModelMetrics(db *sql.DB) {
    metrics := map[string]interface{}{
        "accuracy": rand.Float64()*0.2 + 0.8,
        "precision": rand.Float64()*0.2 + 0.8,
        "recall": rand.Float64()*0.2 + 0.8,
        "f1_score": rand.Float64()*0.2 + 0.8,
    }
    metricsJSON, _ := json.Marshal(metrics)
    
    _, err := db.Exec(`
        INSERT INTO model_metrics (
            model_name, metrics, created_at
        )
        VALUES ($1, $2, $3)
    `, randomChoice([]string{"ctr", "engagement", "satisfaction"}),
        metricsJSON, time.Now())
    
    if err != nil {
        fmt.Println("Model metrics failed:", err)
    }
}

func main() {
    db, err := sql.Open("postgres", dbURL)
    if err != nil {
        panic(err)
    }
    defer db.Close()

    // Seed data
    for i := 0; i < 100; i++ {
        userID := insertUser(db)
        contentID := insertContent(db, userID)
        adID := insertAd(db)
        
        // Generate engagements
        for j := 0; j < rand.Intn(5); j++ {
            insertEngagement(db, userID, contentID)
        }
        
        // Generate ad impressions
        for j := 0; j < rand.Intn(10); j++ {
            insertAdImpression(db, userID, adID)
        }
        
        // Generate moderation data
        if rand.Float64() < 0.1 {
            reportID := fmt.Sprintf("report-%d", rand.Intn(1_000_000))
            insertModerationReport(db, userID, contentID)
            insertModerationAction(db, reportID)
        }
        
        // Generate user satisfaction
        insertUserSatisfaction(db, userID)
        
        // Generate model predictions
        insertModelPrediction(db, userID, contentID)
        
        // Generate model metrics periodically
        if i%10 == 0 {
            insertModelMetrics(db)
        }
    }
}