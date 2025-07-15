from datetime import datetime
from . import db, BaseModel

class DeviceToken(BaseModel):
    __tablename__ = 'user_device_tokens'

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    firebase_device_token = db.Column(db.Text, primary_key=True)
    platform = db.Column(db.Text, nullable=False)
    last_seen_date = db.Column(db.DateTime, nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='device_tokens')

    def __init__(self, user_id, firebase_device_token, platform, last_seen_date=None):
        self.user_id = user_id
        self.firebase_device_token = firebase_device_token
        self.platform = platform
        self.last_seen_date = last_seen_date if last_seen_date else datetime.utcnow()

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'firebase_device_token': self.firebase_device_token,
            'platform': self.platform,
            'last_seen_date': self.last_seen_date.isoformat() if self.last_seen_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def update_last_seen(self):
        """Update the last seen timestamp"""
        self.last_seen_date = datetime.utcnow()
        self.save()

    def __repr__(self):
        return f'<DeviceToken {self.firebase_device_token}>' 