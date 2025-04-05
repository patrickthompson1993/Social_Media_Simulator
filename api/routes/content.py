from fastapi import APIRouter, HTTPException, Depends
from db import get_db
from typing import List, Optional
import json
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Pydantic models for request/response validation
class ContentBase(BaseModel):
    user_id: str
    content_type: str
    content: str
    topic: Optional[str] = None

class ContentCreate(ContentBase):
    pass

class ContentUpdate(BaseModel):
    content: Optional[str] = None
    topic: Optional[str] = None

class ContentInteraction(BaseModel):
    user_id: str
    interaction_type: str
    time_spent_seconds: Optional[int] = None
    scroll_position: Optional[int] = None
    viewport_position: Optional[dict] = None
    device_orientation: Optional[dict] = None

class ContentReport(BaseModel):
    reporter_id: str
    content_id: str
    content_type: str
    report_reason: str
    severity_score: Optional[float] = None

class ContentFlag(BaseModel):
    user_id: str
    content_id: str
    flag_reason: str
    severity_score: Optional[float] = None

# Content endpoints
@router.get("")
def get_all_content(skip: int = 0, limit: int = 100):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, content_type, content, topic, created_at
        FROM posts
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (limit, skip))
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "user_id": row[1],
        "content_type": row[2],
        "content": row[3],
        "topic": row[4],
        "created_at": row[5]
    } for row in rows]

@router.get("/{content_id}")
def get_content_by_id(content_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, content_type, content, topic, created_at
        FROM posts
        WHERE id = %s
    """, (content_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return {
        "id": row[0],
        "user_id": row[1],
        "content_type": row[2],
        "content": row[3],
        "topic": row[4],
        "created_at": row[5]
    }

@router.get("/threads")
def get_all_threads(skip: int = 0, limit: int = 100):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, content, topic, created_at
        FROM posts
        WHERE content_type = 'thread'
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (limit, skip))
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "user_id": row[1],
        "content": row[2],
        "topic": row[3],
        "created_at": row[4]
    } for row in rows]

@router.get("/videos")
def get_all_videos(skip: int = 0, limit: int = 100):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, content, topic, created_at
        FROM posts
        WHERE content_type = 'video'
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (limit, skip))
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "user_id": row[1],
        "content": row[2],
        "topic": row[3],
        "created_at": row[4]
    } for row in rows]

@router.get("/mixed")
def get_mixed_content(skip: int = 0, limit: int = 100):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, content_type, content, topic, created_at
        FROM posts
        WHERE content_type = 'mixed'
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (limit, skip))
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "user_id": row[1],
        "content_type": row[2],
        "content": row[3],
        "topic": row[4],
        "created_at": row[5]
    } for row in rows]

@router.get("/{content_id}/interactions")
def get_content_interactions(content_id: str, interaction_type: Optional[str] = None):
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
        """, (content_id, interaction_type))
    else:
        cur.execute("""
            SELECT user_id, interaction_type, time_spent_seconds,
                   scroll_position, viewport_position, device_orientation,
                   created_at
            FROM content_interactions
            WHERE post_id = %s
            ORDER BY created_at DESC
        """, (content_id,))
    
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

@router.get("/{content_id}/recommendations")
def get_content_recommendations(content_id: str, user_id: Optional[str] = None):
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
        """, (content_id, user_id))
    else:
        cur.execute("""
            SELECT recommendation_source, recommendation_score,
                   recommendation_reason, was_shown, was_engaged,
                   created_at
            FROM content_recommendations
            WHERE post_id = %s
            ORDER BY created_at DESC
        """, (content_id,))
    
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

@router.get("/content-reports")
def get_content_reports(skip: int = 0, limit: int = 100):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, reporter_id, content_id, content_type, report_reason,
               severity_score, status, created_at
        FROM content_reports
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (limit, skip))
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "reporter_id": row[1],
        "content_id": row[2],
        "content_type": row[3],
        "report_reason": row[4],
        "severity_score": row[5],
        "status": row[6],
        "created_at": row[7]
    } for row in rows]

@router.get("/content-reports/{report_id}")
def get_report_by_id(report_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, reporter_id, content_id, content_type, report_reason,
               severity_score, status, created_at
        FROM content_reports
        WHERE id = %s
    """, (report_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "id": row[0],
        "reporter_id": row[1],
        "content_id": row[2],
        "content_type": row[3],
        "report_reason": row[4],
        "severity_score": row[5],
        "status": row[6],
        "created_at": row[7]
    }

@router.get("/content-flags")
def get_content_flags(skip: int = 0, limit: int = 100):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, content_id, flag_reason, severity_score, created_at
        FROM content_flags
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (limit, skip))
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "user_id": row[1],
        "content_id": row[2],
        "flag_reason": row[3],
        "severity_score": row[4],
        "created_at": row[5]
    } for row in rows]

@router.get("/content-flags/{flag_id}")
def get_flag_by_id(flag_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, content_id, flag_reason, severity_score, created_at
        FROM content_flags
        WHERE id = %s
    """, (flag_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Flag not found")
    
    return {
        "id": row[0],
        "user_id": row[1],
        "content_id": row[2],
        "flag_reason": row[3],
        "severity_score": row[4],
        "created_at": row[5]
    }

@router.post("")
def create_content(content: ContentCreate):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO posts (user_id, content_type, content, topic)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (
            content.user_id, content.content_type, content.content, content.topic
        ))
        
        content_id = cur.fetchone()[0]
        conn.commit()
        
        return {"id": content_id, "message": "Content created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.post("/{content_id}/interactions")
def create_content_interaction(content_id: str, interaction: ContentInteraction):
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
            interaction.user_id, content_id, interaction.interaction_type,
            interaction.time_spent_seconds, interaction.scroll_position,
            json.dumps(interaction.viewport_position) if interaction.viewport_position else None,
            json.dumps(interaction.device_orientation) if interaction.device_orientation else None
        ))
        
        interaction_id = cur.fetchone()[0]
        conn.commit()
        
        return {"id": interaction_id, "message": "Interaction recorded successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.post("/content/reports")
def submit_content_report(report: ContentReport):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO content_reports (
                reporter_id, content_id, content_type, report_reason, severity_score, status
            ) VALUES (%s, %s, %s, %s, %s, 'pending')
            RETURNING id
        """, (
            report.reporter_id, report.content_id, report.content_type,
            report.report_reason, report.severity_score
        ))
        
        report_id = cur.fetchone()[0]
        conn.commit()
        
        return {"id": report_id, "message": "Report submitted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.post("/content/flags")
def flag_content(flag: ContentFlag):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO content_flags (
                user_id, content_id, flag_reason, severity_score
            ) VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (
            flag.user_id, flag.content_id, flag.flag_reason, flag.severity_score
        ))
        
        flag_id = cur.fetchone()[0]
        conn.commit()
        
        return {"id": flag_id, "message": "Content flagged successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.put("/{content_id}")
def update_content(content_id: str, content_update: ContentUpdate):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Build update query dynamically based on provided fields
        update_fields = []
        params = []
        
        if content_update.content is not None:
            update_fields.append("content = %s")
            params.append(content_update.content)
        
        if content_update.topic is not None:
            update_fields.append("topic = %s")
            params.append(content_update.topic)
        
        if not update_fields:
            return {"message": "No fields to update"}
        
        # Add content_id to params
        params.append(content_id)
        
        # Execute update
        query = f"""
            UPDATE posts 
            SET {', '.join(update_fields)}
            WHERE id = %s
        """
        cur.execute(query, params)
        
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Content not found")
        
        conn.commit()
        return {"message": "Content updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.delete("/{content_id}")
def delete_content(content_id: str):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Check if content exists
        cur.execute("SELECT id FROM posts WHERE id = %s", (content_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Delete content and related data (cascade should handle this)
        cur.execute("DELETE FROM posts WHERE id = %s", (content_id,))
        
        conn.commit()
        return {"message": "Content deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close() 