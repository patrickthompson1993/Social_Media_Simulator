import os
import logging
from datetime import datetime
from typing import Dict, Any

from content_interaction import ContentInteractionModel
from feed_ranking import FeedRankingModel
from ctr_model import CTRModel
from utils.feature_engineering import FeatureEngineer
from utils.data_preprocessing import DataPreprocessor
from utils.evaluation import ModelEvaluator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feature_engineer = FeatureEngineer()
        self.data_preprocessor = DataPreprocessor()
        self.evaluator = ModelEvaluator()
        
        # Initialize models
        self.ctr_model = CTRModel()
        self.content_model = ContentInteractionModel()
        self.feed_model = FeedRankingModel()
        
        # Create model directory if it doesn't exist
        os.makedirs("models/saved", exist_ok=True)
        
    def prepare_data(self):
        """Prepare and preprocess data for all models"""
        logger.info("Starting data preparation...")
        
        # Load and preprocess data
        raw_data = self.data_preprocessor.load_data()
        processed_data = self.data_preprocessor.preprocess(raw_data)
        
        # Generate features
        features = self.feature_engineer.generate_features(processed_data)
        
        return features
    
    def train_ctr_model(self, features):
        """Train the CTR prediction model"""
        logger.info("Training CTR model...")
        
        # Prepare CTR-specific features
        ctr_features = self.feature_engineer.prepare_ctr_features(features)
        
        # Train model
        self.ctr_model.train(ctr_features)
        
        # Evaluate model
        metrics = self.evaluator.evaluate_ctr(self.ctr_model, ctr_features)
        logger.info(f"CTR Model Metrics: {metrics}")
        
        # Save model
        self.ctr_model.save("models/saved/ctr_model.pkl")
        
    def train_content_model(self, features):
        """Train the content interaction model"""
        logger.info("Training content interaction model...")
        
        # Prepare content-specific features
        content_features = self.feature_engineer.prepare_content_features(features)
        
        # Train model
        self.content_model.train(content_features)
        
        # Evaluate model
        metrics = self.evaluator.evaluate_content(self.content_model, content_features)
        logger.info(f"Content Model Metrics: {metrics}")
        
        # Save model
        self.content_model.save("models/saved/content_model.pkl")
        
    def train_feed_model(self, features):
        """Train the feed ranking model"""
        logger.info("Training feed ranking model...")
        
        # Prepare feed-specific features
        feed_features = self.feature_engineer.prepare_feed_features(features)
        
        # Train model
        self.feed_model.train(feed_features)
        
        # Evaluate model
        metrics = self.evaluator.evaluate_feed(self.feed_model, feed_features)
        logger.info(f"Feed Model Metrics: {metrics}")
        
        # Save model
        self.feed_model.save("models/saved/feed_model.pkl")
        
    def train_all(self):
        """Train all models"""
        logger.info("Starting model training pipeline...")
        
        # Prepare data
        features = self.prepare_data()
        
        # Train models
        self.train_ctr_model(features)
        self.train_content_model(features)
        self.train_feed_model(features)
        
        logger.info("Model training completed successfully!")

def main():
    # Configuration
    config = {
        "data_path": "data/processed",
        "model_path": "models/saved",
        "random_state": 42,
        "test_size": 0.2,
        "validation_size": 0.1,
    }
    
    # Initialize trainer
    trainer = ModelTrainer(config)
    
    # Train all models
    trainer.train_all()

if __name__ == "__main__":
    main() 