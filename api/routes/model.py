from fastapi import APIRouter, HTTPException, Depends
from db import get_db
from typing import List, Optional
import json
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Pydantic models for request/response validation
class ModelMetricsBase(BaseModel):
    model_name: str
    metric_name: str
    metric_value: float
    timestamp: datetime

class ModelMetricsCreate(ModelMetricsBase):
    pass

class ModelPredictionBase(BaseModel):
    model_name: str
    input_data: dict
    prediction: float
    confidence: float
    timestamp: datetime

class ModelPredictionCreate(ModelPredictionBase):
    pass

# Model endpoints
@router.get("/metrics")
def get_model_metrics(
    model_name: Optional[str] = None,
    metric_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
):
    conn = get_db()
    cur = conn.cursor()
    
    query = """
        SELECT id, model_name, metric_name, metric_value, timestamp
        FROM model_metrics
        WHERE 1=1
    """
    params = []
    
    if model_name:
        query += " AND model_name = %s"
        params.append(model_name)
    
    if metric_name:
        query += " AND metric_name = %s"
        params.append(metric_name)
    
    if start_date:
        query += " AND timestamp >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND timestamp <= %s"
        params.append(end_date)
    
    query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "model_name": row[1],
        "metric_name": row[2],
        "metric_value": row[3],
        "timestamp": row[4]
    } for row in rows]

@router.get("/predictions")
def get_model_predictions(
    model_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
):
    conn = get_db()
    cur = conn.cursor()
    
    query = """
        SELECT id, model_name, input_data, prediction, confidence, timestamp
        FROM model_predictions
        WHERE 1=1
    """
    params = []
    
    if model_name:
        query += " AND model_name = %s"
        params.append(model_name)
    
    if start_date:
        query += " AND timestamp >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND timestamp <= %s"
        params.append(end_date)
    
    query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "model_name": row[1],
        "input_data": row[2],
        "prediction": row[3],
        "confidence": row[4],
        "timestamp": row[5]
    } for row in rows]

@router.post("/metrics")
def create_model_metrics(metrics: ModelMetricsCreate):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO model_metrics (
                model_name, metric_name, metric_value, timestamp
            ) VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (
            metrics.model_name, metrics.metric_name,
            metrics.metric_value, metrics.timestamp
        ))
        
        metrics_id = cur.fetchone()[0]
        conn.commit()
        
        return {"id": metrics_id, "message": "Model metrics recorded successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.post("/predictions")
def create_model_prediction(prediction: ModelPredictionCreate):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO model_predictions (
                model_name, input_data, prediction, confidence, timestamp
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            prediction.model_name, json.dumps(prediction.input_data),
            prediction.prediction, prediction.confidence, prediction.timestamp
        ))
        
        prediction_id = cur.fetchone()[0]
        conn.commit()
        
        return {"id": prediction_id, "message": "Model prediction recorded successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.get("/stats")
def get_model_stats():
    conn = get_db()
    cur = conn.cursor()
    
    # Get metrics statistics
    cur.execute("""
        SELECT 
            model_name,
            metric_name,
            COUNT(*) as count,
            AVG(metric_value) as avg_value,
            MIN(metric_value) as min_value,
            MAX(metric_value) as max_value
        FROM model_metrics
        GROUP BY model_name, metric_name
    """)
    metrics_stats = cur.fetchall()
    
    # Get prediction statistics
    cur.execute("""
        SELECT 
            model_name,
            COUNT(*) as total_predictions,
            AVG(prediction) as avg_prediction,
            AVG(confidence) as avg_confidence
        FROM model_predictions
        GROUP BY model_name
    """)
    prediction_stats = cur.fetchall()
    
    conn.close()
    
    return {
        "metrics": [{
            "model_name": row[0],
            "metric_name": row[1],
            "count": row[2],
            "avg_value": row[3],
            "min_value": row[4],
            "max_value": row[5]
        } for row in metrics_stats],
        "predictions": [{
            "model_name": row[0],
            "total_predictions": row[1],
            "avg_prediction": row[2],
            "avg_confidence": row[3]
        } for row in prediction_stats]
    }
