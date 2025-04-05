import numpy as np
import pandas as pd
from typing import Dict, List, Any
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    ndcg_score
)
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logger = logging.getLogger(__name__)

class ModelEvaluator:
    def __init__(self):
        self.metrics = {}
        self.feature_importance = None
        
    def evaluate_regression(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Evaluate regression model performance"""
        metrics = {
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred)
        }
        
        self.metrics = metrics
        return metrics
        
    def evaluate_classification(self, y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None) -> Dict[str, float]:
        """Evaluate classification model performance"""
        metrics = {
            'precision': precision_score(y_true, y_pred),
            'recall': recall_score(y_true, y_pred),
            'f1': f1_score(y_true, y_pred)
        }
        
        if y_prob is not None:
            metrics['roc_auc'] = roc_auc_score(y_true, y_prob)
            
        self.metrics = metrics
        return metrics
        
    def evaluate_ranking(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Evaluate ranking model performance"""
        metrics = {
            'ndcg': ndcg_score([y_true], [y_pred])
        }
        
        self.metrics = metrics
        return metrics
        
    def plot_feature_importance(self, feature_names: List[str], importance_scores: np.ndarray, top_n: int = 10):
        """Plot feature importance scores"""
        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance_scores
        })
        
        # Sort by importance
        importance_df = importance_df.sort_values('importance', ascending=False)
        
        # Take top N features
        importance_df = importance_df.head(top_n)
        
        # Create plot
        plt.figure(figsize=(10, 6))
        sns.barplot(x='importance', y='feature', data=importance_df)
        plt.title('Top Feature Importance Scores')
        plt.xlabel('Importance Score')
        plt.ylabel('Feature')
        plt.tight_layout()
        
        return plt.gcf()
        
    def plot_prediction_distribution(self, y_true: np.ndarray, y_pred: np.ndarray):
        """Plot distribution of predicted vs actual values"""
        plt.figure(figsize=(10, 6))
        sns.kdeplot(data=y_true, label='Actual', color='blue')
        sns.kdeplot(data=y_pred, label='Predicted', color='red')
        plt.title('Distribution of Actual vs Predicted Values')
        plt.xlabel('Value')
        plt.ylabel('Density')
        plt.legend()
        plt.tight_layout()
        
        return plt.gcf()
        
    def plot_residuals(self, y_true: np.ndarray, y_pred: np.ndarray):
        """Plot residuals vs predicted values"""
        residuals = y_true - y_pred
        
        plt.figure(figsize=(10, 6))
        plt.scatter(y_pred, residuals, alpha=0.5)
        plt.axhline(y=0, color='r', linestyle='--')
        plt.title('Residuals vs Predicted Values')
        plt.xlabel('Predicted Values')
        plt.ylabel('Residuals')
        plt.tight_layout()
        
        return plt.gcf()
        
    def plot_learning_curves(self, train_scores: List[float], val_scores: List[float], metric_name: str):
        """Plot learning curves"""
        plt.figure(figsize=(10, 6))
        plt.plot(train_scores, label='Training')
        plt.plot(val_scores, label='Validation')
        plt.title(f'Learning Curves - {metric_name}')
        plt.xlabel('Iteration')
        plt.ylabel(metric_name)
        plt.legend()
        plt.tight_layout()
        
        return plt.gcf()
        
    def generate_report(self, output_path: str = None) -> str:
        """Generate evaluation report"""
        report = []
        report.append("Model Evaluation Report")
        report.append("=" * 50)
        
        for metric, value in self.metrics.items():
            report.append(f"{metric}: {value:.4f}")
            
        report = "\n".join(report)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)
            logger.info(f"Evaluation report saved to {output_path}")
            
        return report 