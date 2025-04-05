from fastapi import APIRouter, HTTPException, Depends
from db import get_db
from typing import List, Optional
import json
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Pydantic models for request/response validation
class ContentReportBase(BaseModel):
    content_id: str
    reporter_id: str
    report_type: str
    description: str
    severity: str

class ContentReportCreate(ContentReportBase):
    pass

class ContentReportUpdate(BaseModel):
    status: str
    moderator_notes: Optional[str] = None

class ContentFlagBase(BaseModel):
    content_id: str
    flagger_id: str
    flag_type: str
    description: Optional[str] = None

class ContentFlagCreate(ContentFlagBase):
    pass

class ContentFlagUpdate(BaseModel):
    status: str
    moderator_notes: Optional[str] = None

# Moderation endpoints
@router.get("/reports")
def get_content_reports(skip: int = 0, limit: int = 100, status: Optional[str] = None):
    conn = get_db()
    cur = conn.cursor()
    
    query = """
        SELECT id, content_id, reporter_id, report_type, description, severity, status, moderator_notes, created_at
        FROM content_reports
    """
    params = []
    
    if status:
        query += " WHERE status = %s"
        params.append(status)
    
    query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "content_id": row[1],
        "reporter_id": row[2],
        "report_type": row[3],
        "description": row[4],
        "severity": row[5],
        "status": row[6],
        "moderator_notes": row[7],
        "created_at": row[8]
    } for row in rows]

@router.get("/reports/{report_id}")
def get_content_report(report_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, content_id, reporter_id, report_type, description, severity, status, moderator_notes, created_at
        FROM content_reports
        WHERE id = %s
    """, (report_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Content report not found")
    
    return {
        "id": row[0],
        "content_id": row[1],
        "reporter_id": row[2],
        "report_type": row[3],
        "description": row[4],
        "severity": row[5],
        "status": row[6],
        "moderator_notes": row[7],
        "created_at": row[8]
    }

@router.get("/flags")
def get_content_flags(skip: int = 0, limit: int = 100, status: Optional[str] = None):
    conn = get_db()
    cur = conn.cursor()
    
    query = """
        SELECT id, content_id, flagger_id, flag_type, description, status, moderator_notes, created_at
        FROM content_flags
    """
    params = []
    
    if status:
        query += " WHERE status = %s"
        params.append(status)
    
    query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "content_id": row[1],
        "flagger_id": row[2],
        "flag_type": row[3],
        "description": row[4],
        "status": row[5],
        "moderator_notes": row[6],
        "created_at": row[7]
    } for row in rows]

@router.get("/flags/{flag_id}")
def get_content_flag(flag_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, content_id, flagger_id, flag_type, description, status, moderator_notes, created_at
        FROM content_flags
        WHERE id = %s
    """, (flag_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Content flag not found")
    
    return {
        "id": row[0],
        "content_id": row[1],
        "flagger_id": row[2],
        "flag_type": row[3],
        "description": row[4],
        "status": row[5],
        "moderator_notes": row[6],
        "created_at": row[7]
    }

@router.post("/reports")
def create_content_report(report: ContentReportCreate):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO content_reports (
                content_id, reporter_id, report_type, description, severity, status
            ) VALUES (%s, %s, %s, %s, %s, 'pending')
            RETURNING id
        """, (
            report.content_id, report.reporter_id, report.report_type,
            report.description, report.severity
        ))
        
        report_id = cur.fetchone()[0]
        conn.commit()
        
        return {"id": report_id, "message": "Content report created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.post("/flags")
def create_content_flag(flag: ContentFlagCreate):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO content_flags (
                content_id, flagger_id, flag_type, description, status
            ) VALUES (%s, %s, %s, %s, 'pending')
            RETURNING id
        """, (
            flag.content_id, flag.flagger_id, flag.flag_type,
            flag.description
        ))
        
        flag_id = cur.fetchone()[0]
        conn.commit()
        
        return {"id": flag_id, "message": "Content flag created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.put("/reports/{report_id}")
def update_content_report(report_id: str, report_update: ContentReportUpdate):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE content_reports
            SET status = %s, moderator_notes = %s
            WHERE id = %s
        """, (report_update.status, report_update.moderator_notes, report_id))
        
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Content report not found")
        
        conn.commit()
        return {"message": "Content report updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.put("/flags/{flag_id}")
def update_content_flag(flag_id: str, flag_update: ContentFlagUpdate):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE content_flags
            SET status = %s, moderator_notes = %s
            WHERE id = %s
        """, (flag_update.status, flag_update.moderator_notes, flag_id))
        
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Content flag not found")
        
        conn.commit()
        return {"message": "Content flag updated successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.get("/stats")
def get_moderation_stats():
    conn = get_db()
    cur = conn.cursor()
    
    # Get report statistics
    cur.execute("""
        SELECT 
            COUNT(*) as total_reports,
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_reports,
            COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_reports,
            COUNT(CASE WHEN status = 'dismissed' THEN 1 END) as dismissed_reports
        FROM content_reports
    """)
    report_stats = cur.fetchone()
    
    # Get flag statistics
    cur.execute("""
        SELECT 
            COUNT(*) as total_flags,
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_flags,
            COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_flags,
            COUNT(CASE WHEN status = 'dismissed' THEN 1 END) as dismissed_flags
        FROM content_flags
    """)
    flag_stats = cur.fetchone()
    
    conn.close()
    
    return {
        "reports": {
            "total": report_stats[0],
            "pending": report_stats[1],
            "resolved": report_stats[2],
            "dismissed": report_stats[3]
        },
        "flags": {
            "total": flag_stats[0],
            "pending": flag_stats[1],
            "resolved": flag_stats[2],
            "dismissed": flag_stats[3]
        }
    } 