import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class ContentInteractionModel:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_columns = [
            'user_age',
            'user_region_encoded',
            'user_device_encoded',
            'user_persona_id',
            'content_type_encoded',
            'content_topic_encoded',
            'content_length',
            'content_age_hours',
            'user_engagement_score',
            'content_engagement_score',
            'user_satisfaction_score',
            'hour_of_day',
            'day_of_week'
        ]
        
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for training or prediction"""
        # Ensure all required features are present
        missing_cols = set(self.feature_columns) - set(data.columns)
        if missing_cols:
            raise ValueError(f"Missing required features: {missing_cols}")
            
        # Extract features
        X = data[self.feature_columns].values
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        return X
        
    def train(self, data: pd.DataFrame):
        """Train the content interaction model"""
        logger.info("Training content interaction model...")
        
        # Prepare features
        X = self._prepare_features(data)
        y = data['engagement_score'].values
        
        # Train model
        self.model.fit(X, y)
        
        logger.info("Content interaction model training completed")
        
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Predict engagement scores"""
        # Prepare features
        X = self._prepare_features(data)
        
        # Make predictions
        predictions = self.model.predict(X)
        
        return predictions
        
    def evaluate(self, data: pd.DataFrame) -> Dict[str, float]:
        """Evaluate model performance"""
        from sklearn.metrics import mean_squared_error, r2_score
        
        # Make predictions
        predictions = self.predict(data)
        y_true = data['engagement_score'].values
        
        # Calculate metrics
        metrics = {
            'mse': mean_squared_error(y_true, predictions),
            'rmse': np.sqrt(mean_squared_error(y_true, predictions)),
            'r2': r2_score(y_true, predictions)
        }
        
        return metrics
        
    def save(self, path: str):
        """Save model to disk"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")
        
    def load(self, path: str):
        """Load model from disk"""
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        logger.info(f"Model loaded from {path}")
        
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance scores"""
        importance = self.model.feature_importances_
        return pd.DataFrame({
            'feature': self.feature_columns,
            'importance': importance
        }).sort_values('importance', ascending=False) 