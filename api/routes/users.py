from fastapi import APIRouter, HTTPException, Depends
from db import get_db
from typing import List, Optional
import json
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Pydantic models for request/response validation
class UserBase(BaseModel):
    username: str
    email: str
    age: Optional[int] = None
    gender: Optional[str] = None
    region: Optional[str] = None
    device: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    region: Optional[str] = None
    device: Optional[str] = None

class UserPreferences(BaseModel):
    notification_settings: dict
    privacy_settings: dict
    content_preferences: dict
    language_preference: str
    theme_preference: str
    timezone: str

# Existing endpoints
@router.get("/regions")
def get_user_regions():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT region AS label, COUNT(*) FROM users GROUP BY region")
    rows = cur.fetchall()
    conn.close()
    return [{"label": r[0], "count": r[1]} for r in rows]

@router.get("/{user_id}/preferences")
def get_user_preferences(user_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT notification_settings, privacy_settings, content_preferences,
               language_preference, theme_preference, timezone
        FROM user_preferences
        WHERE user_id = %s
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="User preferences not found")
    
    return {
        "notification_settings": json.loads(row[0]),
        "privacy_settings": json.loads(row[1]),
        "content_preferences": json.loads(row[2]),
        "language_preference": row[3],
        "theme_preference": row[4],
        "timezone": row[5]
    }

@router.get("/{user_id}/relationships")
def get_user_relationships(user_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT following_id, relationship_type
        FROM user_relationships
        WHERE follower_id = %s
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "following_id": row[0],
        "relationship_type": row[1]
    } for row in rows]

@router.get("/{user_id}/network-metrics")
def get_user_network_metrics(user_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT follower_count, following_count, engagement_rate,
               network_density, influence_score, community_clusters
        FROM user_network_metrics
        WHERE user_id = %s
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="User network metrics not found")
    
    return {
        "follower_count": row[0],
        "following_count": row[1],
        "engagement_rate": row[2],
        "network_density": row[3],
        "influence_score": row[4],
        "community_clusters": json.loads(row[5])
    }

# New endpoints to match README
@router.get("")
def get_all_users(skip: int = 0, limit: int = 100):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, username, email, age, gender, region, device, 
               status, last_active, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (limit, skip))
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "username": row[1],
        "email": row[2],
        "age": row[3],
        "gender": row[4],
        "region": row[5],
        "device": row[6],
        "status": row[7],
        "last_active": row[8],
        "created_at": row[9]
    } for row in rows]

@router.get("/{user_id}")
def get_user_by_id(user_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, username, email, age, gender, region, device, 
               status, last_active, created_at
        FROM users
        WHERE id = %s
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": row[0],
        "username": row[1],
        "email": row[2],
        "age": row[3],
        "gender": row[4],
        "region": row[5],
        "device": row[6],
        "status": row[7],
        "last_active": row[8],
        "created_at": row[9]
    }

@router.get("/{user_id}/metrics")
def get_user_metrics(user_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT avg_scroll_depth, avg_watch_time, clicks_last_24h,
               content_interactions, video_completion_rate, last_updated
        FROM user_metrics
        WHERE user_id = %s
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="User metrics not found")
    
    return {
        "avg_scroll_depth": row[0],
        "avg_watch_time": row[1],
        "clicks_last_24h": row[2],
        "content_interactions": row[3],
        "video_completion_rate": row[4],
        "last_updated": row[5]
    }

@router.get("/{user_id}/churn-events")
def get_user_churn_events(user_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, reason, satisfaction_score, created_at
        FROM churn_events
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "reason": row[1],
        "satisfaction_score": row[2],
        "created_at": row[3]
    } for row in rows]

@router.post("")
def create_user(user: UserCreate):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Insert user
        cur.execute("""
            INSERT INTO users (username, email, age, gender, region, device, status, last_active)
            VALUES (%s, %s, %s, %s, %s, %s, 'active', NOW())
            RETURNING id
        """, (
            user.username, user.email, user.age, user.gender, 
            user.region, user.device
        ))
        
        user_id = cur.fetchone()[0]
        
        # Insert user preferences with defaults
        cur.execute("""
            INSERT INTO user_preferences (user_id, notification_settings, privacy_settings, 
                                         content_preferences, language_preference, theme_preference, timezone)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            json.dumps({"email": True, "push": True, "in_app": True}),
            json.dumps({"profile_visible": True, "activity_visible": True}),
            json.dumps({"topics": [], "content_types": ["thread", "video", "mixed"]}),
            "en",
            "light",
            "UTC"
        ))
        
        # Initialize user metrics
        cur.execute("""
            INSERT INTO user_metrics (user_id, avg_scroll_depth, avg_watch_time, 
                                     clicks_last_24h, content_interactions, video_completion_rate)
            VALUES (%s, 0, 0, 0, 0, 0)
        """, (user_id,))
        
        # Initialize user network metrics
        cur.execute("""
            INSERT INTO user_network_metrics (user_id, follower_count, following_count, 
                                             engagement_rate, network_density, influence_score, community_clusters)
            VALUES (%s, 0, 0, 0, 0, 0, %s)
        """, (user_id, json.dumps([])))
        
        conn.commit()
        
        return {"id": user_id, "message": "User created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.put("/{user_id}")
def update_user(user_id: str, user_update: UserUpdate):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Build update query dynamically based on provided fields
        update_fields = []
        params = []
        
        if user_update.username is not None:
            update_fields.append("username = %s")
            params.append(user_update.username)
        
        if user_update.email is not None:
            update_fields.append("email = %s")
            params.append(user_update.email)
        
        if user_update.age is not None:
            update_fields.append("age = %s")
            params.append(user_update.age)
        
        if user_update.gender is not None:
            update_fields.append("gender = %s")
            params.append(user_update.gender)
        
        if user_update.region is not None:
            update_fields.append("region = %s")
            params.append(user_update.region)
        
        if user_update.device is not None:
            update_fields.append("device = %s")
            params.append(user_update.device)
        
        if not update_fields:
            return {"message": "No fields to update"}
        
        # Add user_id to params
        params.append(user_id)
        
        # Execute update
        query = f"""
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE id = %s
        """
        cur.execute(query, params)
        
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        return {"message": "User updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.put("/{user_id}/preferences")
def update_user_preferences(user_id: str, preferences: UserPreferences):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE user_preferences
            SET notification_settings = %s,
                privacy_settings = %s,
                content_preferences = %s,
                language_preference = %s,
                theme_preference = %s,
                timezone = %s
            WHERE user_id = %s
        """, (
            json.dumps(preferences.notification_settings),
            json.dumps(preferences.privacy_settings),
            json.dumps(preferences.content_preferences),
            preferences.language_preference,
            preferences.theme_preference,
            preferences.timezone,
            user_id
        ))
        
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="User preferences not found")
        
        conn.commit()
        return {"message": "User preferences updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.delete("/{user_id}")
def delete_user(user_id: str):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Check if user exists
        cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete user and related data (cascade should handle this)
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        conn.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
