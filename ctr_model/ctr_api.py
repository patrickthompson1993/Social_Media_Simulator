from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
from typing import Optional
from datetime import datetime

app = FastAPI(
    title="CTR Prediction API",
    description="API for predicting click-through rates for ads",
    version="1.0.0"
)

# Load the model
try:
    model = joblib.load("model.pkl")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

class CTRPredictionRequest(BaseModel):
    ad_id: str
    user_id: str
    feed_position: int
    feed_type: str
    timestamp: Optional[datetime] = None

class CTRPredictionResponse(BaseModel):
    ad_id: str
    user_id: str
    feed_position: int
    feed_type: str
    predicted_ctr: float
    confidence: float
    timestamp: datetime

@app.post("/api/ads/predict/ctr", response_model=CTRPredictionResponse)
async def predict_ctr(data: CTRPredictionRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Extract features from the request
        features = np.array([[
            hash(data.ad_id) % 1000,  # Simple hash for ad_id
            hash(data.user_id) % 1000,  # Simple hash for user_id
            data.feed_position,
            hash(data.feed_type) % 10,  # Simple hash for feed_type
            data.timestamp.hour if data.timestamp else datetime.now().hour
        ]])
        
        # Get prediction and confidence
        prob = model.predict_proba(features)[0][1]  # Probability of click
        confidence = 0.8  # Mock confidence score
        
        return CTRPredictionResponse(
            ad_id=data.ad_id,
            user_id=data.user_id,
            feed_position=data.feed_position,
            feed_type=data.feed_type,
            predicted_ctr=float(round(prob, 4)),
            confidence=float(round(confidence, 4)),
            timestamp=data.timestamp or datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}
