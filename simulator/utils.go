package main

import (
	"math/rand"
	"time"
)

// Random utilities
func randomFloat(min, max float64) float64 {
	return min + rand.Float64()*(max-min)
}

func randomInt(min, max int) int {
	return min + rand.Intn(max-min+1)
}

func randomChoice[T any](choices []T) T {
	return choices[rand.Intn(len(choices))]
}

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

// Time utilities
func randomTimeInRange(start, end time.Time) time.Time {
	delta := end.Sub(start)
	randomDuration := time.Duration(rand.Int63n(int64(delta)))
	return start.Add(randomDuration)
}

func randomDuration(min, max time.Duration) time.Duration {
	return min + time.Duration(rand.Int63n(int64(max-min)))
}

// String utilities
func randomString(length int) string {
	const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	result := make([]byte, length)
	for i := range result {
		result[i] = charset[rand.Intn(len(charset))]
	}
	return string(result)
}

// Math utilities
func min(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}

func max(a, b float64) float64 {
	if a > b {
		return a
	}
	return b
}

func clamp(value, min, max float64) float64 {
	return max(min, min(max, value))
}

// Probability utilities
func randomBool(probability float64) bool {
	return rand.Float64() < probability
}

func randomProbabilities(count int) []float64 {
	probs := make([]float64, count)
	sum := 0.0
	
	// Generate random values
	for i := range probs {
		probs[i] = rand.Float64()
		sum += probs[i]
	}
	
	// Normalize to sum to 1
	for i := range probs {
		probs[i] /= sum
	}
	
	return probs
}

// Map utilities
func mapKeys[K comparable, V any](m map[K]V) []K {
	keys := make([]K, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	return keys
}

func mapValues[K comparable, V any](m map[K]V) []V {
	values := make([]V, 0, len(m))
	for _, v := range m {
		values = append(values, v)
	}
	return values
}

// Slice utilities
func shuffle[T any](slice []T) {
	rand.Shuffle(len(slice), func(i, j int) {
		slice[i], slice[j] = slice[j], slice[i]
	})
}

func sample[T any](slice []T, n int) []T {
	if n >= len(slice) {
		return slice
	}
	
	result := make([]T, n)
	indices := rand.Perm(len(slice))
	
	for i := 0; i < n; i++ {
		result[i] = slice[indices[i]]
	}
	
	return result
}

// Initialize random seed
func init() {
	rand.Seed(time.Now().UnixNano())
} 