import pandas as pd
import numpy as np
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import roc_auc_score, mean_squared_error, precision_recall_curve
import joblib
import json
from datetime import datetime, timedelta
import os
import logging
from sqlalchemy import create_engine, text

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseModel:
    def __init__(self, name):
        self.name = name
        self.model = None
        self.scaler = StandardScaler()
        
    def save_model(self, path):
        if self.model:
            self.model.save_model(f"{path}/{self.name}.pkl")
            np.save(f"{path}/{self.name}_scaler.npy", self.scaler)
            
    def load_model(self, path):
        self.model = joblib.load(f"{path}/{self.name}.pkl")
        self.scaler = np.load(f"{path}/{self.name}_scaler.npy", allow_pickle=True).item()

class ContentInteractionModel(BaseModel):
    def __init__(self):
        super().__init__("content_interaction")
        
    def prepare_features(self, data):
        features = pd.DataFrame()
        
        # User features
        features['user_age'] = data['user_age']
        features['user_satisfaction'] = data['user_satisfaction']
        features['user_engagement_rate'] = data['user_engagement_rate']
        features['user_network_density'] = data['user_network_density']
        features['user_influence_score'] = data['user_influence_score']
        
        # Content features
        features['content_type'] = pd.get_dummies(data['content_type'], prefix='content_type')
        features['content_age_hours'] = (datetime.now() - pd.to_datetime(data['created_at'])).dt.total_seconds() / 3600
        features['content_engagement_rate'] = data['content_engagement_rate']
        features['content_report_count'] = data['content_report_count']
        features['content_flag_score'] = data['content_flag_score']
        
        # Interaction history
        features['user_content_interactions'] = data['user_content_interactions']
        features['user_video_completion_rate'] = data['user_video_completion_rate']
        features['user_avg_watch_time'] = data['user_avg_watch_time']
        
        # Network features
        features['user_follower_count'] = data['user_follower_count']
        features['user_following_count'] = data['user_following_count']
        features['user_community_clusters'] = data['user_community_clusters'].apply(lambda x: json.loads(x)['primary'])
        
        # Moderation features
        features['has_active_flags'] = data['has_active_flags'].astype(int)
        features['moderation_status'] = pd.get_dummies(data['moderation_status'], prefix='moderation')
        
        return features

    def train(self, data, tune_hyperparams=False):
        X = self.prepare_features(data)
        y = data['interaction_label']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        if tune_hyperparams:
            param_grid = {
                'num_leaves': [31, 63, 127],
                'learning_rate': [0.01, 0.05, 0.1],
                'n_estimators': [100, 200, 300],
                'max_depth': [3, 5, 7]
            }
            
            base_model = LGBMClassifier()
            grid_search = GridSearchCV(base_model, param_grid, cv=3, scoring='roc_auc')
            grid_search.fit(X_train_scaled, y_train)
            
            self.model = grid_search.best_estimator_
        else:
            self.model = LGBMClassifier(
                num_leaves=31,
                learning_rate=0.05,
                n_estimators=200,
                max_depth=5
            )
            self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict_proba(X_test_scaled)[:, 1]
        auc = roc_auc_score(y_test, y_pred)
        print(f"Content Interaction Model AUC: {auc:.4f}")

class FeedRankingModel(BaseModel):
    def __init__(self):
        super().__init__("feed_ranking")
        
    def prepare_features(self, data):
        features = pd.DataFrame()
        
        # User features
        features['user_satisfaction'] = data['user_satisfaction']
        features['user_engagement_rate'] = data['user_engagement_rate']
        features['user_network_density'] = data['user_network_density']
        
        # Content features
        features['content_type'] = pd.get_dummies(data['content_type'], prefix='content_type')
        features['content_age_hours'] = (datetime.now() - pd.to_datetime(data['created_at'])).dt.total_seconds() / 3600
        features['content_engagement_rate'] = data['content_engagement_rate']
        
        # Feed features
        features['feed_position'] = data['feed_position']
        features['feed_type'] = pd.get_dummies(data['feed_type'], prefix='feed')
        features['time_spent_seconds'] = data['time_spent_seconds']
        
        # Session features
        features['session_length'] = data['session_length_seconds']
        features['avg_scroll_depth'] = data['avg_scroll_depth']
        features['avg_watch_time'] = data['avg_watch_time']
        
        # Network features
        features['user_follower_count'] = data['user_follower_count']
        features['user_following_count'] = data['user_following_count']
        
        return features

    def train(self, data, tune_hyperparams=False):
        X = self.prepare_features(data)
        y = data['engagement_score']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        if tune_hyperparams:
            param_grid = {
                'num_leaves': [31, 63, 127],
                'learning_rate': [0.01, 0.05, 0.1],
                'n_estimators': [100, 200, 300],
                'max_depth': [3, 5, 7]
            }
            
            base_model = LGBMRegressor()
            grid_search = GridSearchCV(base_model, param_grid, cv=3, scoring='neg_mean_squared_error')
            grid_search.fit(X_train_scaled, y_train)
            
            self.model = grid_search.best_estimator_
        else:
            self.model = LGBMRegressor(
                num_leaves=31,
                learning_rate=0.05,
                n_estimators=200,
                max_depth=5
            )
            self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        print(f"Feed Ranking Model MSE: {mse:.4f}")

class CTRModel(BaseModel):
    def __init__(self):
        super().__init__("ctr")
        
    def prepare_features(self, data):
        features = pd.DataFrame()
        
        # User features
        features['user_age'] = data['user_age']
        features['user_satisfaction'] = data['user_satisfaction']
        features['user_engagement_rate'] = data['user_engagement_rate']
        features['user_network_density'] = data['user_network_density']
        features['user_influence_score'] = data['user_influence_score']
        features['user_device'] = pd.get_dummies(data['user_device'], prefix='device')
        features['user_region'] = pd.get_dummies(data['user_region'], prefix='region')
        
        # User preferences
        features['notification_enabled'] = data['notification_settings'].apply(lambda x: json.loads(x)['enabled'] if isinstance(x, str) else x.get('enabled', 0))
        features['content_preferences'] = data['content_preferences'].apply(lambda x: json.loads(x)['categories'] if isinstance(x, str) else x.get('categories', []))
        
        # Ad features
        features['ad_category'] = pd.get_dummies(data['ad_category'], prefix='ad_category')
        features['ad_content_type'] = pd.get_dummies(data['ad_content_type'], prefix='ad_content')
        features['ad_budget'] = data['ad_budget']
        features['ad_age_hours'] = (datetime.now() - pd.to_datetime(data['created_at'])).dt.total_seconds() / 3600
        
        # Content features
        features['content_type'] = pd.get_dummies(data['content_type'], prefix='content_type')
        features['content_age_hours'] = (datetime.now() - pd.to_datetime(data['content_created_at'])).dt.total_seconds() / 3600
        features['content_engagement_rate'] = data['content_engagement_rate']
        
        # Moderation features
        features['has_active_flags'] = data['has_active_flags'].astype(int)
        features['content_report_count'] = data['content_report_count']
        features['content_flag_score'] = data['content_flag_score']
        features['moderation_status'] = pd.get_dummies(data['moderation_status'], prefix='moderation')
        
        # Position and timing features
        features['feed_position'] = data['feed_position']
        features['feed_type'] = pd.get_dummies(data['feed_type'], prefix='feed')
        features['hour_of_day'] = pd.to_datetime(data['created_at']).dt.hour
        features['day_of_week'] = pd.to_datetime(data['created_at']).dt.dayofweek
        
        # Historical performance
        features['historical_ctr'] = data['historical_ctr']
        features['historical_engagement_rate'] = data['historical_engagement_rate']
        
        # Session features
        features['session_length'] = data['session_length_seconds']
        features['session_position'] = data['session_position']
        features['previous_ads_seen'] = data['previous_ads_seen']
        
        return features

    def train(self, data, tune_hyperparams=False):
        X = self.prepare_features(data)
        y = data['click_label']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        if tune_hyperparams:
            param_grid = {
                'num_leaves': [31, 63, 127],
                'learning_rate': [0.01, 0.05, 0.1],
                'n_estimators': [100, 200, 300],
                'max_depth': [3, 5, 7],
                'min_child_samples': [20, 50, 100],
                'subsample': [0.8, 0.9, 1.0],
                'colsample_bytree': [0.8, 0.9, 1.0]
            }
            
            base_model = LGBMClassifier()
            grid_search = GridSearchCV(base_model, param_grid, cv=3, scoring='roc_auc')
            grid_search.fit(X_train_scaled, y_train)
            
            self.model = grid_search.best_estimator_
        else:
            self.model = LGBMClassifier(
                num_leaves=63,
                learning_rate=0.05,
                n_estimators=200,
                max_depth=5,
                min_child_samples=50,
                subsample=0.9,
                colsample_bytree=0.9
            )
            self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict_proba(X_test_scaled)[:, 1]
        auc = roc_auc_score(y_test, y_pred)
        print(f"CTR Model AUC: {auc:.4f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        print("\nTop 10 Most Important Features:")
        print(feature_importance.head(10))

def load_data_from_db():
    engine = create_engine('postgresql://user:password@localhost:5432/social_media')
    
    # Load user data
    users_query = """
    SELECT u.*, up.notification_settings, up.privacy_settings, up.content_preferences,
           unm.follower_count, unm.following_count, unm.engagement_rate,
           unm.network_density, unm.influence_score, unm.community_clusters
    FROM users u
    LEFT JOIN user_preferences up ON u.id = up.user_id
    LEFT JOIN user_network_metrics unm ON u.id = unm.user_id
    """
    users_df = pd.read_sql(users_query, engine)
    
    # Load content data
    content_query = """
    SELECT p.*, t.reply_count, t.retweet_count, t.quote_count,
           v.duration_seconds, v.completion_rate, v.watch_time_seconds,
           COUNT(cr.id) as report_count,
           COALESCE(cf.flag_score, 0) as flag_score,
           CASE WHEN cf.id IS NOT NULL THEN 1 ELSE 0 END as has_active_flags,
           CASE 
               WHEN ma.action_type = 'remove_content' THEN 'removed'
               WHEN ma.action_type = 'flag_content' THEN 'flagged'
               ELSE 'active'
           END as moderation_status
    FROM posts p
    LEFT JOIN threads t ON p.id = t.post_id
    LEFT JOIN videos v ON p.id = v.post_id
    LEFT JOIN content_reports cr ON p.id = cr.content_id
    LEFT JOIN content_flags cf ON p.id = cf.content_id
    LEFT JOIN moderation_actions ma ON cr.id = ma.report_id
    GROUP BY p.id, t.reply_count, t.retweet_count, t.quote_count,
             v.duration_seconds, v.completion_rate, v.watch_time_seconds,
             cf.flag_score, cf.id, ma.action_type
    """
    content_df = pd.read_sql(content_query, engine)
    
    # Load interaction data
    interaction_query = """
    SELECT ci.*, u.satisfaction_score, u.engagement_rate,
           u.network_density, u.influence_score
    FROM content_interactions ci
    JOIN users u ON ci.user_id = u.id
    """
    interaction_df = pd.read_sql(interaction_query, engine)
    
    # Load feed interaction data
    feed_query = """
    SELECT fi.*, us.session_length_seconds, us.avg_scroll_depth,
           us.avg_watch_time
    FROM feed_interactions fi
    JOIN user_sessions us ON fi.user_id = us.user_id
    """
    feed_df = pd.read_sql(feed_query, engine)
    
    # Load ad data
    ad_query = """
    SELECT a.*, ai.predicted_ctr, ai.actual_click,
           COUNT(cr.id) as report_count,
           COALESCE(cf.flag_score, 0) as flag_score,
           CASE WHEN cf.id IS NOT NULL THEN 1 ELSE 0 END as has_active_flags,
           CASE 
               WHEN ma.action_type = 'remove_content' THEN 'removed'
               WHEN ma.action_type = 'flag_content' THEN 'flagged'
               ELSE 'active'
           END as moderation_status
    FROM ads a
    LEFT JOIN ad_impressions ai ON a.id = ai.ad_id
    LEFT JOIN content_reports cr ON a.id = cr.content_id
    LEFT JOIN content_flags cf ON a.id = cf.content_id
    LEFT JOIN moderation_actions ma ON cr.id = ma.report_id
    GROUP BY a.id, ai.predicted_ctr, ai.actual_click,
             cf.flag_score, cf.id, ma.action_type
    """
    ad_df = pd.read_sql(ad_query, engine)
    
    return users_df, content_df, interaction_df, feed_df, ad_df

def train_all_models(use_db_data=True, tune_hyperparams=False):
    if use_db_data:
        users_df, content_df, interaction_df, feed_df, ad_df = load_data_from_db()
    else:
        # Generate synthetic data
        users_df = generate_users(1000)
        content_df = generate_content(5000)
        interaction_df = generate_interactions(users_df, content_df)
        feed_df = generate_feed_interactions(users_df, content_df)
        ad_df = generate_ads(100)
    
    # Train Content Interaction Model
    content_model = ContentInteractionModel()
    content_model.train(interaction_df, tune_hyperparams)
    content_model.save_model("models")
    
    # Train Feed Ranking Model
    feed_model = FeedRankingModel()
    feed_model.train(feed_df, tune_hyperparams)
    feed_model.save_model("models")
    
    # Train CTR Model
    ctr_model = CTRModel()
    ctr_model.train(ad_df, tune_hyperparams)
    ctr_model.save_model("models")

if __name__ == "__main__":
    train_all_models(use_db_data=True, tune_hyperparams=True) 