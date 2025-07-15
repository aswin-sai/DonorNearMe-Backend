from db import db
from datetime import datetime

class Donation(db.Model):
    __tablename__ = 'donations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blood_request_id = db.Column(db.Integer, db.ForeignKey('blood_requests.id'), nullable=True)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    certificate = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='donations')
    blood_request = db.relationship('BloodRequest', backref='donations') 