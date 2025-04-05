from datetime import datetime
import uuid

class Post:
    def __init__(self, id=None, user_id=None, content_type=None, content=None, 
                 topic=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.content_type = content_type
        self.content = content
        self.topic = topic
        self.created_at = created_at or datetime.now()
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_type': self.content_type,
            'content': self.content,
            'topic': self.topic,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        return cls(**data)

class Thread:
    def __init__(self, id=None, post_id=None, parent_thread_id=None, is_thread_start=False, 
                 thread_position=None, reply_count=0, retweet_count=0, quote_count=0, 
                 created_at=None):
        self.id = id or str(uuid.uuid4())
        self.post_id = post_id
        self.parent_thread_id = parent_thread_id
        self.is_thread_start = is_thread_start
        self.thread_position = thread_position
        self.reply_count = reply_count
        self.retweet_count = retweet_count
        self.quote_count = quote_count
        self.created_at = created_at or datetime.now()
        
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'parent_thread_id': self.parent_thread_id,
            'is_thread_start': self.is_thread_start,
            'thread_position': self.thread_position,
            'reply_count': self.reply_count,
            'retweet_count': self.retweet_count,
            'quote_count': self.quote_count,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        return cls(**data)

class Video:
    def __init__(self, post_id=None, duration_seconds=None, resolution=None, 
                 thumbnail_url=None, video_url=None, sound_url=None, is_muted=False, 
                 completion_rate=0.0, watch_time_seconds=0, loop_count=0, created_at=None):
        self.post_id = post_id
        self.duration_seconds = duration_seconds
        self.resolution = resolution
        self.thumbnail_url = thumbnail_url
        self.video_url = video_url
        self.sound_url = sound_url
        self.is_muted = is_muted
        self.completion_rate = completion_rate
        self.watch_time_seconds = watch_time_seconds
        self.loop_count = loop_count
        self.created_at = created_at or datetime.now()
        
    def to_dict(self):
        return {
            'post_id': self.post_id,
            'duration_seconds': self.duration_seconds,
            'resolution': self.resolution,
            'thumbnail_url': self.thumbnail_url,
            'video_url': self.video_url,
            'sound_url': self.sound_url,
            'is_muted': self.is_muted,
            'completion_rate': self.completion_rate,
            'watch_time_seconds': self.watch_time_seconds,
            'loop_count': self.loop_count,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        return cls(**data) 