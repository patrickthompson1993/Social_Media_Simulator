# Machine Learning Models

This directory contains the machine learning models used for content recommendation, feed ranking, and click-through rate prediction.

## Models

### 1. Content Interaction Model
- Predicts user engagement with content
- Uses Random Forest Regressor
- Features include user demographics, content metadata, and historical engagement

### 2. Feed Ranking Model
- Ranks content items for user feed
- Uses Gradient Boosting Regressor
- Features include predicted engagement, content quality, and user preferences

### 3. CTR Model
- Predicts click-through rates for content
- Uses Gradient Boosting Classifier
- Features include content metadata, user behavior, and historical CTR

## Directory Structure

```
models/
├── train_models.py          # Main training script
├── content_interaction.py   # Content interaction model
├── feed_ranking.py         # Feed ranking model
├── ctr_model.py            # CTR prediction model
├── utils/
│   ├── feature_engineering.py  # Feature engineering utilities
│   ├── data_preprocessing.py   # Data preprocessing utilities
│   └── evaluation.py          # Model evaluation utilities
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Training Models

To train all models:
```bash
python train_models.py
```

To train a specific model:
```bash
python train_models.py --model ctr
python train_models.py --model content_interaction
python train_models.py --model feed_ranking
```

### Model Evaluation

Models are automatically evaluated during training. Evaluation metrics include:
- Regression metrics (MSE, RMSE, MAE, R²)
- Classification metrics (Precision, Recall, F1, ROC AUC)
- Ranking metrics (NDCG)

### Feature Engineering

The feature engineering module (`utils/feature_engineering.py`) handles:
- Categorical feature encoding
- Derived feature calculation
- Feature normalization
- Time-based feature extraction

### Data Preprocessing

The data preprocessing module (`utils/data_preprocessing.py`) handles:
- Data loading and cleaning
- Missing value imputation
- Outlier removal
- Train-test splitting
- Data preparation for training

## Model Persistence

Models are saved using joblib and can be loaded for inference:
```python
from ctr_model import CTRModel
model = CTRModel()
model.load('models/ctr_model.joblib')
predictions = model.predict(data)
```

## Contributing

1. Follow PEP 8 style guide
2. Add docstrings to all functions and classes
3. Include unit tests for new features
4. Update documentation as needed

## License

This project is licensed under the MIT License - see the LICENSE file for details. 