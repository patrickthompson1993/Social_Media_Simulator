import pandas as pd
import numpy as np
import lightgbm as lgb
import joblib
from datetime import datetime, timedelta

personas = [
    {"name": "Teen Gamer", "category": 0, "night": 1, "mobile": 1, "boost": 0.15},
    {"name": "Political Boomer", "category": 1, "night": 0, "mobile": 0, "boost": 0.12},
    {"name": "Meme Lord", "category": 2, "night": 1, "mobile": 1, "boost": 0.14},
    {"name": "Budget Shopper", "category": 3, "night": 1, "mobile": 0, "boost": 0.10},
    {"name": "News Junkie", "category": 4, "night": 0, "mobile": 1, "boost": 0.08},
    {"name": "Influencer Watcher", "category": 5, "night": 1, "mobile": 1, "boost": 0.13},
    {"name": "Crypto Bro", "category": 6, "night": 1, "mobile": 1, "boost": 0.09},
    {"name": "Skeptic", "category": 7, "night": 0, "mobile": 0, "boost": 0.02},
    {"name": "Impulse Buyer", "category": 8, "night": 1, "mobile": 1, "boost": 0.18},
    {"name": "Tech Professional", "category": 9, "night": 0, "mobile": 0, "boost": 0.10},
    {"name": "Parent", "category": 10, "night": 0, "mobile": 1, "boost": 0.09},
    {"name": "Eco Enthusiast", "category": 11, "night": 0, "mobile": 0, "boost": 0.07},
    {"name": "Luxury Lover", "category": 12, "night": 1, "mobile": 0, "boost": 0.12},
    {"name": "Sports Fan", "category": 13, "night": 1, "mobile": 1, "boost": 0.11},
    {"name": "Gadget Geek", "category": 14, "night": 1, "mobile": 0, "boost": 0.13},
    {"name": "Entrepreneur", "category": 15, "night": 0, "mobile": 0, "boost": 0.08},
    {"name": "Educator", "category": 16, "night": 0, "mobile": 0, "boost": 0.06},
    {"name": "Student", "category": 17, "night": 1, "mobile": 1, "boost": 0.14},
    {"name": "Retiree", "category": 18, "night": 0, "mobile": 0, "boost": 0.05},
    {"name": "Generalist", "category": 19, "night": 1, "mobile": 1, "boost": 0.10},
    {"name": "Fitness Enthusiast", "category": 20, "night": 0, "mobile": 1, "boost": 0.16},
    {"name": "Foodie", "category": 21, "night": 1, "mobile": 1, "boost": 0.15},
    {"name": "Travel Blogger", "category": 22, "night": 1, "mobile": 1, "boost": 0.14},
    {"name": "Art Collector", "category": 23, "night": 0, "mobile": 0, "boost": 0.11},
    {"name": "Music Lover", "category": 24, "night": 1, "mobile": 1, "boost": 0.13},
    {"name": "Bookworm", "category": 25, "night": 0, "mobile": 0, "boost": 0.09},
    {"name": "Pet Owner", "category": 26, "night": 1, "mobile": 1, "boost": 0.17},
    {"name": "Home Decorator", "category": 27, "night": 0, "mobile": 1, "boost": 0.12},
    {"name": "Car Enthusiast", "category": 28, "night": 0, "mobile": 0, "boost": 0.10},
    {"name": "Fashionista", "category": 29, "night": 1, "mobile": 1, "boost": 0.16},
    {"name": "Gamer Pro", "category": 30, "night": 1, "mobile": 0, "boost": 0.15},
    {"name": "Movie Buff", "category": 31, "night": 1, "mobile": 0, "boost": 0.12},
    {"name": "Photography Enthusiast", "category": 32, "night": 0, "mobile": 1, "boost": 0.11},
    {"name": "DIY Crafter", "category": 33, "night": 0, "mobile": 0, "boost": 0.10},
    {"name": "Garden Enthusiast", "category": 34, "night": 0, "mobile": 0, "boost": 0.09},
    {"name": "Tech Reviewer", "category": 35, "night": 0, "mobile": 0, "boost": 0.13},
    {"name": "Business Professional", "category": 36, "night": 0, "mobile": 0, "boost": 0.11},
    {"name": "Health Conscious", "category": 37, "night": 0, "mobile": 1, "boost": 0.14},
    {"name": "Social Activist", "category": 38, "night": 0, "mobile": 1, "boost": 0.10},
    {"name": "Language Learner", "category": 39, "night": 0, "mobile": 1, "boost": 0.09},
    {"name": "Podcast Listener", "category": 40, "night": 1, "mobile": 1, "boost": 0.12},
    {"name": "Coffee Enthusiast", "category": 41, "night": 0, "mobile": 1, "boost": 0.11},
    {"name": "Wine Connoisseur", "category": 42, "night": 1, "mobile": 0, "boost": 0.13},
    {"name": "Beer Aficionado", "category": 43, "night": 1, "mobile": 0, "boost": 0.12},
    {"name": "Cooking Enthusiast", "category": 44, "night": 0, "mobile": 1, "boost": 0.15},
    {"name": "Yoga Practitioner", "category": 45, "night": 0, "mobile": 1, "boost": 0.14},
    {"name": "Meditation Enthusiast", "category": 46, "night": 0, "mobile": 1, "boost": 0.10},
    {"name": "Astrology Follower", "category": 47, "night": 1, "mobile": 1, "boost": 0.13},
    {"name": "Horoscope Reader", "category": 48, "night": 1, "mobile": 1, "boost": 0.12},
    {"name": "Tarot Card Reader", "category": 49, "night": 1, "mobile": 1, "boost": 0.11},
    {"name": "Crystal Collector", "category": 50, "night": 0, "mobile": 0, "boost": 0.10},
    {"name": "Vintage Collector", "category": 51, "night": 0, "mobile": 0, "boost": 0.09},
    {"name": "Antique Enthusiast", "category": 52, "night": 0, "mobile": 0, "boost": 0.08},
    {"name": "Comic Book Fan", "category": 53, "night": 1, "mobile": 0, "boost": 0.12},
    {"name": "Anime Fan", "category": 54, "night": 1, "mobile": 1, "boost": 0.14},
    {"name": "Manga Reader", "category": 55, "night": 1, "mobile": 1, "boost": 0.13},
    {"name": "Fantasy Reader", "category": 56, "night": 0, "mobile": 0, "boost": 0.11},
    {"name": "Sci-Fi Enthusiast", "category": 57, "night": 0, "mobile": 0, "boost": 0.10},
    {"name": "Horror Fan", "category": 58, "night": 1, "mobile": 0, "boost": 0.12},
    {"name": "Romance Novel Reader", "category": 59, "night": 0, "mobile": 1, "boost": 0.13},
    {"name": "Mystery Enthusiast", "category": 60, "night": 0, "mobile": 0, "boost": 0.11},
    {"name": "Thriller Fan", "category": 61, "night": 1, "mobile": 0, "boost": 0.12},
    {"name": "Biography Reader", "category": 62, "night": 0, "mobile": 0, "boost": 0.09},
    {"name": "History Buff", "category": 63, "night": 0, "mobile": 0, "boost": 0.08},
    {"name": "Science Enthusiast", "category": 64, "night": 0, "mobile": 0, "boost": 0.10},
    {"name": "Math Enthusiast", "category": 65, "night": 0, "mobile": 0, "boost": 0.09},
    {"name": "Philosophy Student", "category": 66, "night": 0, "mobile": 0, "boost": 0.08},
    {"name": "Psychology Enthusiast", "category": 67, "night": 0, "mobile": 1, "boost": 0.11},
    {"name": "Sociology Student", "category": 68, "night": 0, "mobile": 1, "boost": 0.10},
    {"name": "Anthropology Enthusiast", "category": 69, "night": 0, "mobile": 0, "boost": 0.09}
]

def generate(n=10000):
    X, y = [], []
    for _ in range(n):
        pid = np.random.randint(0, len(personas))
        p = personas[pid]
        
        # Basic user features
        age = np.random.randint(12, 80)
        hour = np.random.randint(0, 24)
        device = 0 if p["mobile"] else np.random.randint(0, 2)
        category = np.random.randint(0, 20)
        match = 1 if category == p["category"] else 0
        feed_pos = np.random.randint(1, 11)
        
        # User metrics from user_metrics table
        avg_scroll_depth = np.random.uniform(0.1, 1.0)
        avg_watch_time = np.random.uniform(10, 300)
        clicks_last_24h = np.random.randint(0, 50)
        content_interactions = np.random.randint(0, 20)
        video_completion_rate = np.random.uniform(0.1, 1.0)
        
        # Network metrics from user_network_metrics table
        follower_count = np.random.randint(0, 1000)
        following_count = np.random.randint(0, 1000)
        engagement_rate = np.random.uniform(0.1, 0.9)
        network_density = np.random.uniform(0.1, 0.8)
        influence_score = np.random.uniform(0.1, 10.0)
        
        # Time-based features
        day_of_week = np.random.randint(0, 7)
        is_weekend = 1 if day_of_week >= 5 else 0
        
        # Content moderation features
        has_active_flags = np.random.randint(0, 2)
        flag_score = np.random.uniform(0, 1.0) if has_active_flags else 0
        report_count = np.random.randint(0, 5)
        moderation_status = np.random.randint(0, 4)  # 0: clean, 1: flagged, 2: under_review, 3: restricted
        
        # Calculate base CTR with more factors
        base = 0.03
        
        # Time-based factors
        if hour >= 20 or hour <= 2:
            base += 0.04 if p["night"] else -0.01
        if is_weekend:
            base += 0.02
            
        # User engagement factors
        if match:
            base += p["boost"]
        if device == 0 and p["mobile"]:
            base += 0.03
        if feed_pos <= 3:
            base += 0.02
            
        # User metrics factors
        base += avg_scroll_depth * 0.03
        base += min(avg_watch_time / 300, 1.0) * 0.02
        base += min(clicks_last_24h / 50, 1.0) * 0.03
        base += min(content_interactions / 20, 1.0) * 0.02
        base += video_completion_rate * 0.03
        
        # Network metrics factors
        base += min(follower_count / 1000, 1.0) * 0.02
        base += min(following_count / 1000, 1.0) * 0.01
        base += engagement_rate * 0.03
        base += network_density * 0.02
        base += min(influence_score / 10, 1.0) * 0.04
        
        # Content moderation factors
        if has_active_flags:
            base -= flag_score * 0.1
        if report_count > 0:
            base -= min(report_count * 0.05, 0.2)
        if moderation_status > 0:
            base -= moderation_status * 0.05
        
        # Add noise
        noise = np.random.normal(0, 0.01)
        click_prob = max(0.01, min(base + noise, 1.0))

        X.append([
            pid, age, device, hour, category, feed_pos, match,
            avg_scroll_depth, avg_watch_time, clicks_last_24h,
            content_interactions, video_completion_rate,
            follower_count, following_count, engagement_rate,
            network_density, influence_score,
            day_of_week, is_weekend,
            has_active_flags, flag_score, report_count, moderation_status
        ])
        y.append(click_prob)
        
    return pd.DataFrame(X, columns=[
        "persona_id", "age", "device", "hour", "ad_category", "feed_position", "match",
        "avg_scroll_depth", "avg_watch_time", "clicks_last_24h",
        "content_interactions", "video_completion_rate",
        "follower_count", "following_count", "engagement_rate",
        "network_density", "influence_score",
        "day_of_week", "is_weekend",
        "has_active_flags", "flag_score", "report_count", "moderation_status"
    ]), y

def train():
    X, y = generate()
    model = lgb.LGBMRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        num_leaves=31,
        feature_fraction=0.8,
        bagging_fraction=0.8,
        bagging_freq=5
    )
    model.fit(X, y)
    joblib.dump(model, "model.pkl")
    print("Saved model.pkl")

if __name__ == "__main__":
    train()
