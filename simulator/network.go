package main

import (
	"time"
)

// SimulateNetworkGrowth simulates network growth for a user
func SimulateNetworkGrowth(user User) error {
	// Load potential connections from database
	query := `
		SELECT user_id, network_density, influence_score
		FROM users
		WHERE user_id != $1 AND status = 'active'
		ORDER BY RANDOM()
		LIMIT 20
	`

	rows, err := db.Query(query, user.ID)
	if err != nil {
		return ErrDatabaseQuery("load_potential_connections", err)
	}
	defer rows.Close()

	var potentialConnections []struct {
		UserID        string
		NetworkDensity float64
		InfluenceScore float64
	}

	for rows.Next() {
		var connection struct {
			UserID        string
			NetworkDensity float64
			InfluenceScore float64
		}

		err := rows.Scan(
			&connection.UserID,
			&connection.NetworkDensity,
			&connection.InfluenceScore,
		)
		if err != nil {
			return ErrDatabaseQuery("scan_potential_connection", err)
		}

		potentialConnections = append(potentialConnections, connection)
	}

	if err = rows.Err(); err != nil {
		return ErrDatabaseQuery("iterate_potential_connections", err)
	}

	// Simulate connection formation
	for _, connection := range potentialConnections {
		// Calculate connection probability
		connectionProb := 0.1 // Base probability
		
		// Adjust based on network density
		connectionProb += (user.NetworkDensity + connection.NetworkDensity) * 0.2
		
		// Adjust based on influence score
		connectionProb += min(user.InfluenceScore, connection.InfluenceScore) / 20
		
		// Determine if connection is formed
		if randomBool(connectionProb) {
			// Check if connection already exists
			var exists bool
			err := db.QueryRow(`
				SELECT EXISTS(
					SELECT 1 FROM user_connections 
					WHERE (user_id = $1 AND connection_id = $2) OR (user_id = $2 AND connection_id = $1)
				)
			`, user.ID, connection.UserID).Scan(&exists)
			if err != nil {
				return ErrDatabaseQuery("check_existing_connection", err)
			}
			
			if !exists {
				// Save connection to database
				_, err := db.Exec(`
					INSERT INTO user_connections (user_id, connection_id, created_at)
					VALUES ($1, $2, $3)
				`, user.ID, connection.UserID, time.Now())
				if err != nil {
					return ErrDatabaseQuery("save_connection", err)
				}
				
				// Update user network density
				user.NetworkDensity += 0.05
				if user.NetworkDensity > 1.0 {
					user.NetworkDensity = 1.0
				}
				
				// Log network action
				LogNetworkAction(user.ID, "new_connection", connection.UserID)
			}
		}
	}

	return nil
}

// SimulateUserChurn simulates user churn
func SimulateUserChurn(user User) bool {
	// Calculate churn probability
	churnProb := config.ChurnBaseProbability
	
	// Adjust based on satisfaction
	churnProb += (1.0 - user.Satisfaction) * 0.5
	
	// Adjust based on engagement rate
	churnProb += (1.0 - user.EngagementRate) * 0.3
	
	// Adjust based on network density
	churnProb += (1.0 - user.NetworkDensity) * 0.2
	
	// Determine if user churns
	if randomBool(churnProb) {
		// Update user status in database
		_, err := db.Exec(`
			UPDATE users 
			SET status = 'inactive', last_active = $1
			WHERE user_id = $2
		`, time.Now(), user.ID)
		if err != nil {
			LogError("Failed to update user status: %v", err)
		}
		
		// Update metrics
		UpdateMetrics(func(m *Metrics) {
			m.ActiveUsers--
			m.ChurnedUsers++
		})
		
		return true
	}
	
	return false
}

// shouldReportContent determines if a user should report content
func shouldReportContent(user User, ad Ad) bool {
	// Base probability from config
	reportProb := config.ReportProbability
	
	// Adjust based on user satisfaction
	reportProb += (1.0 - user.Satisfaction) * 0.3
	
	// Adjust based on content category
	if preferences, ok := user.Preferences["categories"].([]interface{}); ok {
		for _, category := range preferences {
			if cat, ok := category.(float64); ok && int(cat) == ad.Category {
				reportProb *= 0.8 // Less likely to report content from preferred categories
				break
			}
		}
	}
	
	// Determine if content should be reported
	return randomBool(reportProb)
} 