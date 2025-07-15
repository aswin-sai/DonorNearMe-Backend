from db import db

class UserDeviceToken(db.Model):
    __tablename__ = 'user_device_tokens'

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    firebase_device_token = db.Column(db.Text, primary_key=True)
    platform = db.Column(db.Text, nullable=False)
    last_seen_date = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref='device_tokens')

    def __init__(self, user_id, firebase_device_token, platform, last_seen_date=None):
        self.user_id = user_id
        self.firebase_device_token = firebase_device_token
        self.platform = platform
        self.last_seen_date = last_seen_date

    def __repr__(self):
        return f'<UserDeviceToken {self.firebase_device_token}>'