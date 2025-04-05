from fastapi import APIRouter, HTTPException, Depends
from db import get_db
from typing import List, Optional
import json
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter()

# Pydantic models for request/response validation
class UserSatisfactionBase(BaseModel):
    user_id: str
    satisfaction_score: float
    timestamp: datetime

class UserSatisfactionCreate(UserSatisfactionBase):
    pass

class EngagementMetricsBase(BaseModel):
    date: datetime
    likes: int
    comments: int
    shares: int
    bookmarks: int

class EngagementMetricsCreate(EngagementMetricsBase):
    pass

class AdROIBase(BaseModel):
    date: datetime
    ad_id: str
    impressions: int
    clicks: int
    revenue: float
    cost: float

class AdROICreate(AdROIBase):
    pass

# Expanded metrics endpoints
@router.get("/users/satisfaction")
def get_user_satisfaction_distribution():
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            CASE 
                WHEN satisfaction_score >= 4 THEN 'High'
                WHEN satisfaction_score >= 2 THEN 'Medium'
                ELSE 'Low'
            END as satisfaction_level,
            COUNT(*) as count
        FROM user_satisfaction
        GROUP BY 
            CASE 
                WHEN satisfaction_score >= 4 THEN 'High'
                WHEN satisfaction_score >= 2 THEN 'Medium'
                ELSE 'Low'
            END
        ORDER BY 
            CASE satisfaction_level
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
            END
    """)
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "satisfaction_level": row[0],
        "count": row[1]
    } for row in rows]

@router.get("/engagement/timeseries")
def get_engagement_timeseries(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    interval: str = 'day'
):
    conn = get_db()
    cur = conn.cursor()
    
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    query = """
        SELECT 
            DATE_TRUNC(%s, timestamp) as time_bucket,
            COUNT(CASE WHEN interaction_type = 'like' THEN 1 END) as likes,
            COUNT(CASE WHEN interaction_type = 'comment' THEN 1 END) as comments,
            COUNT(CASE WHEN interaction_type = 'share' THEN 1 END) as shares,
            COUNT(CASE WHEN interaction_type = 'bookmark' THEN 1 END) as bookmarks
        FROM content_interactions
        WHERE timestamp BETWEEN %s AND %s
        GROUP BY time_bucket
        ORDER BY time_bucket
    """
    
    cur.execute(query, (interval, start_date, end_date))
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "timestamp": row[0],
        "likes": row[1],
        "comments": row[2],
        "shares": row[3],
        "bookmarks": row[4]
    } for row in rows]

@router.get("/ads/roi")
def get_ad_roi_trend(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    ad_id: Optional[str] = None
):
    conn = get_db()
    cur = conn.cursor()
    
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    query = """
        SELECT 
            DATE(created_at) as date,
            ad_id,
            COUNT(*) as impressions,
            COUNT(CASE WHEN actual_click THEN 1 END) as clicks,
            SUM(price_paid) as cost,
            SUM(CASE WHEN actual_click THEN price_paid * 2 ELSE 0 END) as revenue
        FROM ad_impressions
        WHERE created_at BETWEEN %s AND %s
    """
    params = [start_date, end_date]
    
    if ad_id:
        query += " AND ad_id = %s"
        params.append(ad_id)
    
    query += " GROUP BY DATE(created_at), ad_id ORDER BY date"
    
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "date": row[0],
        "ad_id": row[1],
        "impressions": row[2],
        "clicks": row[3],
        "cost": row[4],
        "revenue": row[5],
        "roi": (row[5] - row[4]) / row[4] if row[4] > 0 else 0
    } for row in rows]

@router.get("/insights")
def get_smart_insights():
    conn = get_db()
    cur = conn.cursor()
    
    insights = []
    
    # User engagement insight
    cur.execute("""
        SELECT 
            DATE_TRUNC('day', timestamp) as date,
            COUNT(*) as total_interactions,
            COUNT(DISTINCT user_id) as unique_users
        FROM content_interactions
        WHERE timestamp >= NOW() - INTERVAL '7 days'
        GROUP BY date
        ORDER BY date DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    if row:
        avg_interactions_per_user = row[1] / row[2] if row[2] > 0 else 0
        insights.append({
            "type": "user_engagement",
            "metric": "avg_interactions_per_user",
            "value": avg_interactions_per_user,
            "trend": "up" if avg_interactions_per_user > 5 else "down",
            "description": f"Average of {avg_interactions_per_user:.1f} interactions per user in the last 24 hours"
        })
    
    # Content performance insight
    cur.execute("""
        SELECT 
            content_type,
            COUNT(*) as total_interactions,
            COUNT(DISTINCT user_id) as unique_users
        FROM content_interactions
        WHERE timestamp >= NOW() - INTERVAL '7 days'
        GROUP BY content_type
        ORDER BY total_interactions DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    if row:
        insights.append({
            "type": "content_performance",
            "metric": "best_performing_content",
            "value": row[0],
            "trend": "up",
            "description": f"{row[0]} content has the highest engagement with {row[1]} total interactions"
        })
    
    # Ad performance insight
    cur.execute("""
        SELECT 
            ad_id,
            COUNT(*) as impressions,
            COUNT(CASE WHEN actual_click THEN 1 END) as clicks,
            AVG(predicted_ctr) as avg_predicted_ctr,
            AVG(CASE WHEN actual_click THEN 1 ELSE 0 END) as actual_ctr
        FROM ad_impressions
        WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY ad_id
        HAVING COUNT(*) > 100
        ORDER BY actual_ctr DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    if row:
        insights.append({
            "type": "ad_performance",
            "metric": "best_performing_ad",
            "value": row[0],
            "trend": "up" if row[4] > row[3] else "down",
            "description": f"Ad {row[0]} has the highest CTR at {row[4]:.2%} (predicted: {row[3]:.2%})"
        })
    
    conn.close()
    return insights

@router.post("/users/satisfaction")
def create_user_satisfaction(satisfaction: UserSatisfactionCreate):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO user_satisfaction (
                user_id, satisfaction_score, timestamp
            ) VALUES (%s, %s, %s)
            RETURNING id
        """, (
            satisfaction.user_id, satisfaction.satisfaction_score,
            satisfaction.timestamp
        ))
        
        satisfaction_id = cur.fetchone()[0]
        conn.commit()
        
        return {"id": satisfaction_id, "message": "User satisfaction recorded successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.post("/engagement")
def create_engagement_metrics(metrics: EngagementMetricsCreate):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO engagement_metrics (
                date, likes, comments, shares, bookmarks
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            metrics.date, metrics.likes, metrics.comments,
            metrics.shares, metrics.bookmarks
        ))
        
        metrics_id = cur.fetchone()[0]
        conn.commit()
        
        return {"id": metrics_id, "message": "Engagement metrics recorded successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.post("/ads/roi")
def create_ad_roi(roi: AdROICreate):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO ad_roi (
                date, ad_id, impressions, clicks, revenue, cost
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            roi.date, roi.ad_id, roi.impressions,
            roi.clicks, roi.revenue, roi.cost
        ))
        
        roi_id = cur.fetchone()[0]
        conn.commit()
        
        return {"id": roi_id, "message": "Ad ROI recorded successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
