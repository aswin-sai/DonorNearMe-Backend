from db import db
from datetime import datetime

class BloodRequest(db.Model):
    __tablename__ = 'blood_requests'
    blood_request_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.hospital_id'), nullable=False)
    blood_group_type = db.Column(db.Integer, db.ForeignKey('lookup_blood_groups.blood_group_id'), nullable=False)
    no_of_units = db.Column(db.Integer, nullable=False)
    patient_name = db.Column(db.String(120), nullable=False)
    patient_contact_email = db.Column(db.String(120), nullable=True)
    patient_contact_phone_number = db.Column(db.String(20), nullable=True)
    required_by_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')
    from_date = db.Column(db.Date, nullable=True)
    to_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='blood_requests')
    hospital = db.relationship('Hospital', backref='blood_requests')
    blood_group = db.relationship('LookupBloodGroup', backref='blood_requests')

    def __init__(self, user_id, hospital_id, blood_group_type, no_of_units, patient_name, **kwargs):
        self.user_id = user_id
        self.hospital_id = hospital_id
        self.blood_group_type = blood_group_type
        self.no_of_units = no_of_units
        self.patient_name = patient_name
        for key, value in kwargs.items():
            setattr(self, key, value)


class BloodRequestResponse(db.Model):
    __tablename__ = 'blood_requests_responses'

    blood_requests_response_id = db.Column(db.Integer, primary_key=True)
    blood_request_id = db.Column(db.Integer, db.ForeignKey('blood_requests.blood_request_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    response_status = db.Column(db.Text, nullable=False)
    message = db.Column(db.Text, nullable=True)
    from_date = db.Column(db.Date, nullable=False)
    responded_date = db.Column(db.Date, nullable=True)
    to_date = db.Column(db.Date, nullable=True)
    scheduled_datetime = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    blood_request = db.relationship('BloodRequest', backref='responses')
    user = db.relationship('User', backref='responses')

    def __init__(self, blood_request_id, user_id, response_status, from_date, scheduled_datetime=None, **kwargs):
        self.blood_request_id = blood_request_id
        self.user_id = user_id
        self.response_status = response_status
        self.from_date = from_date
        self.scheduled_datetime = scheduled_datetime
        for key, value in kwargs.items():
            setattr(self, key, value)