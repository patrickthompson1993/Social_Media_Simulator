package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// PredictCTR predicts the click-through rate for an ad
func PredictCTR(user User, ad Ad, position int) float64 {
	request := CTRRequest{
		UserID: user.ID,
		AdID:   ad.ID,
		UserMetrics: map[string]float64{
			"satisfaction":        user.Satisfaction,
			"engagement_rate":     user.EngagementRate,
			"network_density":     user.NetworkDensity,
			"influence_score":     user.InfluenceScore,
			"scroll_depth":        user.AvgScrollDepth,
			"watch_time":          user.AvgWatchTime,
			"clicks_last_24h":     float64(user.ClicksLast24h),
			"content_interactions": float64(user.ContentInteractions),
			"completion_rate":      user.VideoCompletionRate,
		},
		AdMetrics: map[string]float64{
			"bid":    ad.Bid,
			"budget": ad.Budget,
		},
		Context: map[string]interface{}{
			"position": position,
			"device":   user.Device,
			"hour":     user.Hour,
			"region":   user.Region,
		},
	}

	response, err := sendRequest(config.CTREndpoint, request)
	if err != nil {
		LogError("Failed to predict CTR: %v", err)
		return 0.1 // Default CTR
	}

	var ctrResponse CTRResponse
	err = json.Unmarshal(response, &ctrResponse)
	if err != nil {
		LogError("Failed to parse CTR response: %v", err)
		return 0.1 // Default CTR
	}

	return ctrResponse.CTR
}

// PredictContentInteraction predicts user interaction with content
func PredictContentInteraction(user User, content DBContent) ContentResponse {
	request := ContentRequest{
		UserID:      user.ID,
		ContentID:   content.ID,
		ContentType: content.ContentType,
		UserMetrics: map[string]float64{
			"satisfaction":        user.Satisfaction,
			"engagement_rate":     user.EngagementRate,
			"network_density":     user.NetworkDensity,
			"influence_score":     user.InfluenceScore,
			"scroll_depth":        user.AvgScrollDepth,
			"watch_time":          user.AvgWatchTime,
			"clicks_last_24h":     float64(user.ClicksLast24h),
			"content_interactions": float64(user.ContentInteractions),
			"completion_rate":      user.VideoCompletionRate,
		},
		ContentMetrics: map[string]float64{
			"reply_count":     float64(content.ReplyCount),
			"retweet_count":   float64(content.RetweetCount),
			"quote_count":     float64(content.QuoteCount),
			"completion_rate": content.CompletionRate,
			"watch_time":      float64(content.WatchTime),
			"loop_count":      float64(content.LoopCount),
		},
		Context: map[string]interface{}{
			"device": user.Device,
			"hour":   user.Hour,
			"region": user.Region,
		},
	}

	response, err := sendRequest(config.ContentEndpoint, request)
	if err != nil {
		LogError("Failed to predict content interaction: %v", err)
		return ContentResponse{
			InteractionProb: 0.3,
			CompletionProb:  0.4,
			EngagementScore: 0.5,
		}
	}

	var contentResponse ContentResponse
	err = json.Unmarshal(response, &contentResponse)
	if err != nil {
		LogError("Failed to parse content response: %v", err)
		return ContentResponse{
			InteractionProb: 0.3,
			CompletionProb:  0.4,
			EngagementScore: 0.5,
		}
	}

	return contentResponse
}

// PredictFeedEngagement predicts user engagement with feed
func PredictFeedEngagement(user User) FeedResponse {
	request := FeedRequest{
		UserID: user.ID,
		UserMetrics: map[string]float64{
			"satisfaction":        user.Satisfaction,
			"engagement_rate":     user.EngagementRate,
			"network_density":     user.NetworkDensity,
			"influence_score":     user.InfluenceScore,
			"scroll_depth":        user.AvgScrollDepth,
			"watch_time":          user.AvgWatchTime,
			"clicks_last_24h":     float64(user.ClicksLast24h),
			"content_interactions": float64(user.ContentInteractions),
			"completion_rate":      user.VideoCompletionRate,
		},
		FeedMetrics: map[string]float64{
			"avg_reply_count":   0.0, // These would be calculated from recent feed
			"avg_retweet_count": 0.0,
			"avg_quote_count":   0.0,
			"avg_completion":    0.0,
			"avg_watch_time":    0.0,
		},
		Context: map[string]interface{}{
			"device": user.Device,
			"hour":   user.Hour,
			"region": user.Region,
		},
	}

	response, err := sendRequest(config.FeedRankingEndpoint, request)
	if err != nil {
		LogError("Failed to predict feed engagement: %v", err)
		return FeedResponse{
			EngagementProb: 0.3,
			ScrollDepth:    0.5,
			TimeSpent:      60.0,
		}
	}

	var feedResponse FeedResponse
	err = json.Unmarshal(response, &feedResponse)
	if err != nil {
		LogError("Failed to parse feed response: %v", err)
		return FeedResponse{
			EngagementProb: 0.3,
			ScrollDepth:    0.5,
			TimeSpent:      60.0,
		}
	}

	return feedResponse
}

// Helper function to send HTTP requests
func sendRequest(endpoint string, request interface{}) ([]byte, error) {
	jsonData, err := json.Marshal(request)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %v", err)
	}

	resp, err := http.Post(endpoint, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to send request: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("request failed with status: %d", resp.StatusCode)
	}

	var response []byte
	_, err = resp.Body.Read(response)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %v", err)
	}

	return response, nil
} 