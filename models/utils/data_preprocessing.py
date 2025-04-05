import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.model_selection import train_test_split
import logging

logger = logging.getLogger(__name__)

class DataPreprocessor:
    def __init__(self, test_size: float = 0.2, random_state: int = 42):
        self.test_size = test_size
        self.random_state = random_state
        
    def load_and_preprocess(self, data_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load and preprocess data from file"""
        logger.info(f"Loading data from {data_path}")
        
        # Load data
        data = pd.read_csv(data_path)
        
        # Basic preprocessing
        data = self._basic_preprocessing(data)
        
        # Split into train and test sets
        train_data, test_data = self._split_data(data)
        
        return train_data, test_data
        
    def _basic_preprocessing(self, data: pd.DataFrame) -> pd.DataFrame:
        """Perform basic preprocessing steps"""
        logger.info("Performing basic preprocessing...")
        
        # Convert timestamps to datetime
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        # Handle missing values
        data = self._handle_missing_values(data)
        
        # Remove outliers
        data = self._remove_outliers(data)
        
        # Add time-based features
        data = self._add_time_features(data)
        
        return data
        
    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset"""
        # For numerical columns, fill with median
        numerical_cols = data.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            data[col] = data[col].fillna(data[col].median())
            
        # For categorical columns, fill with mode
        categorical_cols = data.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            data[col] = data[col].fillna(data[col].mode()[0])
            
        return data
        
    def _remove_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """Remove outliers using IQR method"""
        numerical_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numerical_cols:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            data = data[(data[col] >= lower_bound) & (data[col] <= upper_bound)]
            
        return data
        
    def _add_time_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features"""
        data['hour'] = data['timestamp'].dt.hour
        data['day'] = data['timestamp'].dt.day
        data['month'] = data['timestamp'].dt.month
        data['year'] = data['timestamp'].dt.year
        data['dayofweek'] = data['timestamp'].dt.dayofweek
        data['is_weekend'] = data['dayofweek'].isin([5, 6]).astype(int)
        
        return data
        
    def _split_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split data into train and test sets"""
        logger.info(f"Splitting data into train ({1-self.test_size}) and test ({self.test_size}) sets...")
        
        # Sort by timestamp to ensure chronological split
        data = data.sort_values('timestamp')
        
        # Calculate split index
        split_idx = int(len(data) * (1 - self.test_size))
        
        # Split data
        train_data = data.iloc[:split_idx]
        test_data = data.iloc[split_idx:]
        
        return train_data, test_data
        
    def prepare_training_data(self, data: pd.DataFrame, target_col: str) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for model training"""
        # Separate features and target
        X = data.drop(columns=[target_col, 'timestamp'])
        y = data[target_col]
        
        # Convert to numpy arrays
        X = X.values
        y = y.values
        
        return X, y
        
    def prepare_prediction_data(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare data for model prediction"""
        # Drop timestamp column
        X = data.drop(columns=['timestamp'])
        
        # Convert to numpy array
        X = X.values
        
        return X 