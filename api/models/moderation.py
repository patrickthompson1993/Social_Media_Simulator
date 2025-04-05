from datetime import datetime
import uuid

class ContentReport:
    def __init__(self, id=None, reporter_id=None, content_id=None, content_type=None, 
                 report_reason=None, report_details=None, severity_score=None, 
                 status=None, created_at=None, resolved_at=None):
        self.id = id or str(uuid.uuid4())
        self.reporter_id = reporter_id
        self.content_id = content_id
        self.content_type = content_type
        self.report_reason = report_reason
        self.report_details = report_details
        self.severity_score = severity_score
        self.status = status
        self.created_at = created_at or datetime.now()
        self.resolved_at = resolved_at
        
    def to_dict(self):
        return {
            'id': self.id,
            'reporter_id': self.reporter_id,
            'content_id': self.content_id,
            'content_type': self.content_type,
            'report_reason': self.report_reason,
            'report_details': self.report_details,
            'severity_score': self.severity_score,
            'status': self.status,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'resolved_at': self.resolved_at.isoformat() if isinstance(self.resolved_at, datetime) else self.resolved_at
        }
    
    @classmethod
    def from_dict(cls, data):
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        if 'resolved_at' in data and isinstance(data['resolved_at'], str) and data['resolved_at']:
            data['resolved_at'] = datetime.fromisoformat(data['resolved_at'].replace('Z', '+00:00'))
        return cls(**data)

class ModerationAction:
    def __init__(self, id=None, report_id=None, moderator_id=None, action_type=None, 
                 action_details=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.report_id = report_id
        self.moderator_id = moderator_id
        self.action_type = action_type
        self.action_details = action_details
        self.created_at = created_at or datetime.now()
        
    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'moderator_id': self.moderator_id,
            'action_type': self.action_type,
            'action_details': self.action_details,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        return cls(**data)

class ContentFlag:
    def __init__(self, id=None, content_id=None, content_type=None, flag_type=None, 
                 flag_reason=None, flag_score=None, created_at=None, expires_at=None):
        self.id = id or str(uuid.uuid4())
        self.content_id = content_id
        self.content_type = content_type
        self.flag_type = flag_type
        self.flag_reason = flag_reason
        self.flag_score = flag_score
        self.created_at = created_at or datetime.now()
        self.expires_at = expires_at
        
    def to_dict(self):
        return {
            'id': self.id,
            'content_id': self.content_id,
            'content_type': self.content_type,
            'flag_type': self.flag_type,
            'flag_reason': self.flag_reason,
            'flag_score': self.flag_score,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'expires_at': self.expires_at.isoformat() if isinstance(self.expires_at, datetime) else self.expires_at
        }
    
    @classmethod
    def from_dict(cls, data):
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        if 'expires_at' in data and isinstance(data['expires_at'], str) and data['expires_at']:
            data['expires_at'] = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
        return cls(**data) 