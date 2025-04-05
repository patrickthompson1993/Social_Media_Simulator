import pandas as pd
import numpy as np
from typing import Dict, List, Any
from sklearn.preprocessing import LabelEncoder
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    def __init__(self):
        self.label_encoders = {}
        self.region_encoder = LabelEncoder()
        self.device_encoder = LabelEncoder()
        self.content_type_encoder = LabelEncoder()
        self.topic_encoder = LabelEncoder()
        
    def fit_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Fit encoders and transform data"""
        logger.info("Fitting feature encoders...")
        
        # Encode categorical features
        data['user_region_encoded'] = self.region_encoder.fit_transform(data['user_region'])
        data['user_device_encoded'] = self.device_encoder.fit_transform(data['user_device'])
        data['content_type_encoded'] = self.content_type_encoder.fit_transform(data['content_type'])
        data['content_topic_encoded'] = self.topic_encoder.fit_transform(data['content_topic'])
        
        # Calculate derived features
        data = self._calculate_derived_features(data)
        
        return data
        
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform data using fitted encoders"""
        # Encode categorical features
        data['user_region_encoded'] = self.region_encoder.transform(data['user_region'])
        data['user_device_encoded'] = self.device_encoder.transform(data['user_device'])
        data['content_type_encoded'] = self.content_type_encoder.transform(data['content_type'])
        data['content_topic_encoded'] = self.topic_encoder.transform(data['content_topic'])
        
        # Calculate derived features
        data = self._calculate_derived_features(data)
        
        return data
        
    def _calculate_derived_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived features"""
        # User engagement score
        data['user_engagement_score'] = (
            data['likes'] * 1.0 +
            data['comments'] * 2.0 +
            data['shares'] * 3.0 +
            data['bookmarks'] * 4.0
        ) / 4.0
        
        # Content engagement score
        data['content_engagement_score'] = (
            data['content_likes'] * 1.0 +
            data['content_comments'] * 2.0 +
            data['content_shares'] * 3.0 +
            data['content_bookmarks'] * 4.0
        ) / 4.0
        
        # User satisfaction score (normalized)
        data['user_satisfaction_score'] = data['user_satisfaction'] / 5.0
        
        # Content quality score
        data['content_quality_score'] = (
            data['content_engagement_score'] * 0.7 +
            data['user_satisfaction_score'] * 0.3
        )
        
        # User interest score (based on historical engagement with similar content)
        data['user_interest_score'] = self._calculate_user_interest_score(data)
        
        # Content diversity score
        data['content_diversity_score'] = self._calculate_content_diversity_score(data)
        
        # Time-based features
        data['hour_of_day'] = pd.to_datetime(data['timestamp']).dt.hour
        data['day_of_week'] = pd.to_datetime(data['timestamp']).dt.dayofweek
        
        return data
        
    def _calculate_user_interest_score(self, data: pd.DataFrame) -> pd.Series:
        """Calculate user interest score based on historical engagement"""
        # Group by user and content topic
        user_topic_engagement = data.groupby(['user_id', 'content_topic']).agg({
            'user_engagement_score': 'mean'
        }).reset_index()
        
        # Calculate average engagement per topic
        topic_avg_engagement = user_topic_engagement.groupby('content_topic')['user_engagement_score'].mean()
        
        # Normalize scores
        topic_avg_engagement = (topic_avg_engagement - topic_avg_engagement.min()) / (topic_avg_engagement.max() - topic_avg_engagement.min())
        
        # Map scores back to original data
        return data['content_topic'].map(topic_avg_engagement)
        
    def _calculate_content_diversity_score(self, data: pd.DataFrame) -> pd.Series:
        """Calculate content diversity score"""
        # Group by user and calculate topic diversity
        user_topics = data.groupby('user_id')['content_topic'].nunique()
        
        # Normalize scores
        user_topics = (user_topics - user_topics.min()) / (user_topics.max() - user_topics.min())
        
        # Map scores back to original data
        return data['user_id'].map(user_topics)
        
    def save(self, path: str):
        """Save encoders to disk"""
        import joblib
        encoders = {
            'region_encoder': self.region_encoder,
            'device_encoder': self.device_encoder,
            'content_type_encoder': self.content_type_encoder,
            'topic_encoder': self.topic_encoder
        }
        joblib.dump(encoders, path)
        logger.info(f"Feature encoders saved to {path}")
        
    def load(self, path: str):
        """Load encoders from disk"""
        import joblib
        encoders = joblib.load(path)
        self.region_encoder = encoders['region_encoder']
        self.device_encoder = encoders['device_encoder']
        self.content_type_encoder = encoders['content_type_encoder']
        self.topic_encoder = encoders['topic_encoder']
        logger.info(f"Feature encoders loaded from {path}") 