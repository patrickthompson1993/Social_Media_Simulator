from datetime import datetime
import uuid

class Ad:
    def __init__(self, id=None, advertiser_id=None, title=None, ad_category=None, 
                 content=None, content_type=None, budget=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.advertiser_id = advertiser_id
        self.title = title
        self.ad_category = ad_category
        self.content = content
        self.content_type = content_type
        self.budget = budget
        self.created_at = created_at or datetime.now()
        
    def to_dict(self):
        return {
            'id': self.id,
            'advertiser_id': self.advertiser_id,
            'title': self.title,
            'ad_category': self.ad_category,
            'content': self.content,
            'content_type': self.content_type,
            'budget': self.budget,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        return cls(**data)

class AdImpression:
    def __init__(self, id=None, ad_id=None, user_id=None, feed_position=None, 
                 feed_type=None, predicted_ctr=None, actual_click=None, 
                 price_paid=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.ad_id = ad_id
        self.user_id = user_id
        self.feed_position = feed_position
        self.feed_type = feed_type
        self.predicted_ctr = predicted_ctr
        self.actual_click = actual_click
        self.price_paid = price_paid
        self.created_at = created_at or datetime.now()
        
    def to_dict(self):
        return {
            'id': self.id,
            'ad_id': self.ad_id,
            'user_id': self.user_id,
            'feed_position': self.feed_position,
            'feed_type': self.feed_type,
            'predicted_ctr': self.predicted_ctr,
            'actual_click': self.actual_click,
            'price_paid': self.price_paid,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        return cls(**data)

class AdAuctionLog:
    def __init__(self, id=None, ad_id=None, user_id=None, feed_position=None, 
                 feed_type=None, predicted_ctr=None, actual_click=None, 
                 price_paid=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.ad_id = ad_id
        self.user_id = user_id
        self.feed_position = feed_position
        self.feed_type = feed_type
        self.predicted_ctr = predicted_ctr
        self.actual_click = actual_click
        self.price_paid = price_paid
        self.created_at = created_at or datetime.now()
        
    def to_dict(self):
        return {
            'id': self.id,
            'ad_id': self.ad_id,
            'user_id': self.user_id,
            'feed_position': self.feed_position,
            'feed_type': self.feed_type,
            'predicted_ctr': self.predicted_ctr,
            'actual_click': self.actual_click,
            'price_paid': self.price_paid,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        return cls(**data) 