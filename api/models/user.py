from datetime import datetime
import uuid

class User:
    def __init__(self, id=None, username=None, email=None, age=None, gender=None, 
                 eye_color=None, hair_color=None, weight=None, skin_tone=None, 
                 political_leaning=None, region=None, device=None, persona_id=None, 
                 satisfaction_score=1.0, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.username = username
        self.email = email
        self.age = age
        self.gender = gender
        self.eye_color = eye_color
        self.hair_color = hair_color
        self.weight = weight
        self.skin_tone = skin_tone
        self.political_leaning = political_leaning
        self.region = region
        self.device = device
        self.persona_id = persona_id
        self.satisfaction_score = satisfaction_score
        self.created_at = created_at or datetime.now()
        
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'age': self.age,
            'gender': self.gender,
            'eye_color': self.eye_color,
            'hair_color': self.hair_color,
            'weight': self.weight,
            'skin_tone': self.skin_tone,
            'political_leaning': self.political_leaning,
            'region': self.region,
            'device': self.device,
            'persona_id': self.persona_id,
            'satisfaction_score': self.satisfaction_score,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        return cls(**data) 