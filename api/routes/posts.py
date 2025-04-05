from fastapi import APIRouter, HTTPException
from db import get_db
from typing import List, Optional
import json

router = APIRouter()

@router.get("/{post_id}/interactions")
def get_post_interactions(post_id: str, interaction_type: Optional[str] = None):
    conn = get_db()
    cur = conn.cursor()
    
    if interaction_type:
        cur.execute("""
            SELECT user_id, interaction_type, time_spent_seconds,
                   scroll_position, viewport_position, device_orientation,
                   created_at
            FROM content_interactions
            WHERE post_id = %s AND interaction_type = %s
            ORDER BY created_at DESC
        """, (post_id, interaction_type))
    else:
        cur.execute("""
            SELECT user_id, interaction_type, time_spent_seconds,
                   scroll_position, viewport_position, device_orientation,
                   created_at
            FROM content_interactions
            WHERE post_id = %s
            ORDER BY created_at DESC
        """, (post_id,))
    
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "user_id": row[0],
        "interaction_type": row[1],
        "time_spent_seconds": row[2],
        "scroll_position": row[3],
        "viewport_position": json.loads(row[4]),
        "device_orientation": json.loads(row[5]),
        "created_at": row[6]
    } for row in rows]

@router.get("/{post_id}/recommendations")
def get_post_recommendations(post_id: str, user_id: Optional[str] = None):
    conn = get_db()
    cur = conn.cursor()
    
    if user_id:
        cur.execute("""
            SELECT recommendation_source, recommendation_score,
                   recommendation_reason, was_shown, was_engaged,
                   created_at
            FROM content_recommendations
            WHERE post_id = %s AND user_id = %s
            ORDER BY created_at DESC
        """, (post_id, user_id))
    else:
        cur.execute("""
            SELECT recommendation_source, recommendation_score,
                   recommendation_reason, was_shown, was_engaged,
                   created_at
            FROM content_recommendations
            WHERE post_id = %s
            ORDER BY created_at DESC
        """, (post_id,))
    
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "recommendation_source": row[0],
        "recommendation_score": row[1],
        "recommendation_reason": json.loads(row[2]),
        "was_shown": row[3],
        "was_engaged": row[4],
        "created_at": row[5]
    } for row in rows]

@router.post("/{post_id}/interactions")
def create_post_interaction(
    post_id: str,
    user_id: str,
    interaction_type: str,
    time_spent_seconds: int,
    scroll_position: int,
    viewport_position: dict,
    device_orientation: dict
):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO content_interactions (
                user_id, post_id, interaction_type, time_spent_seconds,
                scroll_position, viewport_position, device_orientation
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            user_id, post_id, interaction_type, time_spent_seconds,
            scroll_position, json.dumps(viewport_position),
            json.dumps(device_orientation)
        ))
        
        interaction_id = cur.fetchone()[0]
        conn.commit()
        
        return {"id": interaction_id, "message": "Interaction recorded successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
