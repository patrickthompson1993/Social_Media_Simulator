from fastapi import APIRouter, HTTPException, Depends
from db import get_db
from typing import List, Optional
import json
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Pydantic models for request/response validation
class AdBase(BaseModel):
    advertiser_id: str
    title: str
    ad_category: str
    content: str
    content_type: str
    budget: float

class AdCreate(AdBase):
    pass

class AdUpdate(BaseModel):
    title: Optional[str] = None
    ad_category: Optional[str] = None
    content: Optional[str] = None
    content_type: Optional[str] = None
    budget: Optional[float] = None

class AdImpression(BaseModel):
    user_id: str
    feed_position: int
    feed_type: str
    predicted_ctr: float
    actual_click: bool
    price_paid: float

class CTRPrediction(BaseModel):
    ad_id: str
    user_id: str
    feed_position: int
    feed_type: str

# Ad endpoints
@router.get("")
def get_all_ads(skip: int = 0, limit: int = 100):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, advertiser_id, title, ad_category, content, content_type, budget, created_at
        FROM ads
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (limit, skip))
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "advertiser_id": row[1],
        "title": row[2],
        "ad_category": row[3],
        "content": row[4],
        "content_type": row[5],
        "budget": row[6],
        "created_at": row[7]
    } for row in rows]

@router.get("/{ad_id}")
def get_ad_by_id(ad_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, advertiser_id, title, ad_category, content, content_type, budget, created_at
        FROM ads
        WHERE id = %s
    """, (ad_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    return {
        "id": row[0],
        "advertiser_id": row[1],
        "title": row[2],
        "ad_category": row[3],
        "content": row[4],
        "content_type": row[5],
        "budget": row[6],
        "created_at": row[7]
    }

@router.get("/{ad_id}/impressions")
def get_ad_impressions(ad_id: str, skip: int = 0, limit: int = 100):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, feed_position, feed_type, predicted_ctr, actual_click, price_paid, created_at
        FROM ad_impressions
        WHERE ad_id = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (ad_id, limit, skip))
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "user_id": row[1],
        "feed_position": row[2],
        "feed_type": row[3],
        "predicted_ctr": row[4],
        "actual_click": row[5],
        "price_paid": row[6],
        "created_at": row[7]
    } for row in rows]

@router.get("/{ad_id}/auction-logs")
def get_ad_auction_logs(ad_id: str, skip: int = 0, limit: int = 100):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, feed_position, feed_type, predicted_ctr, actual_click, price_paid, created_at
        FROM ad_auction_logs
        WHERE ad_id = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (ad_id, limit, skip))
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "user_id": row[1],
        "feed_position": row[2],
        "feed_type": row[3],
        "predicted_ctr": row[4],
        "actual_click": row[5],
        "price_paid": row[6],
        "created_at": row[7]
    } for row in rows]

@router.get("/categories")
def get_ad_categories():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT ad_category, COUNT(*) as count
        FROM ads
        GROUP BY ad_category
        ORDER BY count DESC
    """)
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "category": row[0],
        "count": row[1]
    } for row in rows]

@router.post("")
def create_ad(ad: AdCreate):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO ads (advertiser_id, title, ad_category, content, content_type, budget)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            ad.advertiser_id, ad.title, ad.ad_category, ad.content, 
            ad.content_type, ad.budget
        ))
        
        ad_id = cur.fetchone()[0]
        conn.commit()
        
        return {"id": ad_id, "message": "Ad created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.post("/{ad_id}/impressions")
def record_ad_impression(ad_id: str, impression: AdImpression):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Record impression
        cur.execute("""
            INSERT INTO ad_impressions (
                ad_id, user_id, feed_position, feed_type, predicted_ctr, actual_click, price_paid
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            ad_id, impression.user_id, impression.feed_position, impression.feed_type,
            impression.predicted_ctr, impression.actual_click, impression.price_paid
        ))
        
        impression_id = cur.fetchone()[0]
        
        # Also record in auction logs
        cur.execute("""
            INSERT INTO ad_auction_logs (
                ad_id, user_id, feed_position, feed_type, predicted_ctr, actual_click, price_paid
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            ad_id, impression.user_id, impression.feed_position, impression.feed_type,
            impression.predicted_ctr, impression.actual_click, impression.price_paid
        ))
        
        conn.commit()
        
        return {"id": impression_id, "message": "Ad impression recorded successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.post("/predict/ctr")
def predict_ctr(prediction: CTRPrediction):
    # This would typically call a machine learning model
    # For now, we'll return a mock prediction
    return {
        "ad_id": prediction.ad_id,
        "user_id": prediction.user_id,
        "feed_position": prediction.feed_position,
        "feed_type": prediction.feed_type,
        "predicted_ctr": 0.15  # Mock value
    }

@router.put("/{ad_id}")
def update_ad(ad_id: str, ad_update: AdUpdate):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Build update query dynamically based on provided fields
        update_fields = []
        params = []
        
        if ad_update.title is not None:
            update_fields.append("title = %s")
            params.append(ad_update.title)
        
        if ad_update.ad_category is not None:
            update_fields.append("ad_category = %s")
            params.append(ad_update.ad_category)
        
        if ad_update.content is not None:
            update_fields.append("content = %s")
            params.append(ad_update.content)
        
        if ad_update.content_type is not None:
            update_fields.append("content_type = %s")
            params.append(ad_update.content_type)
        
        if ad_update.budget is not None:
            update_fields.append("budget = %s")
            params.append(ad_update.budget)
        
        if not update_fields:
            return {"message": "No fields to update"}
        
        # Add ad_id to params
        params.append(ad_id)
        
        # Execute update
        query = f"""
            UPDATE ads 
            SET {', '.join(update_fields)}
            WHERE id = %s
        """
        cur.execute(query, params)
        
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ad not found")
        
        conn.commit()
        return {"message": "Ad updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.delete("/{ad_id}")
def delete_ad(ad_id: str):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Check if ad exists
        cur.execute("SELECT id FROM ads WHERE id = %s", (ad_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Ad not found")
        
        # Delete ad and related data (cascade should handle this)
        cur.execute("DELETE FROM ads WHERE id = %s", (ad_id,))
        
        conn.commit()
        return {"message": "Ad deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

# Keep the existing CTR trend endpoint
@router.get("/ctr")
def ctr_trend():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT DATE(created_at), ROUND(AVG(predicted_ctr), 4)
        FROM ad_auction_logs
        GROUP BY DATE(created_at)
        ORDER BY DATE(created_at)
        LIMIT 14
    """)
    data = cur.fetchall()
    conn.close()
    return [{"label": str(d[0]), "values": [d[1]]} for d in data]
