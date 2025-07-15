from datetime import date, datetime
from . import db, BaseModel

class BloodRequest(BaseModel):
    __tablename__ = 'blood_requests'

    blood_request_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.hospital_id'), nullable=False)
    blood_group_type = db.Column(db.Integer, db.ForeignKey('lookup_blood_groups.blood_group_id'), nullable=False)
    no_of_units = db.Column(db.Integer, nullable=False)
    patient_name = db.Column(db.Text, nullable=False)
    patient_contact_email = db.Column(db.Text, nullable=True)
    patient_contact_phone_number = db.Column(db.Text, nullable=True)
    required_by_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, active, completed, cancelled
    from_date = db.Column(db.Date, nullable=False, default=date.today)
    to_date = db.Column(db.Date, nullable=True)

    # Relationships
    requester = db.relationship('User', back_populates='blood_requests')
    hospital = db.relationship('Hospital', back_populates='blood_requests')
    blood_group = db.relationship('LookupBloodGroup')
    responses = db.relationship('BloodRequestResponse', back_populates='blood_request', cascade='all, delete-orphan')

    def __init__(self, user_id, hospital_id, blood_group_type, no_of_units, patient_name, required_by_date, **kwargs):
        self.user_id = user_id
        self.hospital_id = hospital_id
        self.blood_group_type = blood_group_type
        self.no_of_units = no_of_units
        self.patient_name = patient_name
        self.required_by_date = required_by_date
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            'blood_request_id': self.blood_request_id,
            'user_id': self.user_id,
            'hospital_id': self.hospital_id,
            'blood_group_type': self.blood_group_type,
            'no_of_units': self.no_of_units,
            'patient_name': self.patient_name,
            'patient_contact_email': self.patient_contact_email,
            'patient_contact_phone_number': self.patient_contact_phone_number,
            'required_by_date': self.required_by_date.isoformat() if self.required_by_date else None,
            'description': self.description,
            'status': self.status,
            'from_date': self.from_date.isoformat() if self.from_date else None,
            'to_date': self.to_date.isoformat() if self.to_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'requester': self.requester.to_dict() if self.requester else None,
            'hospital': self.hospital.to_dict() if self.hospital else None,
            'blood_group': self.blood_group.to_dict() if self.blood_group else None,
            'responses_count': len(self.responses) if self.responses else 0,
        }

    def is_active(self):
        """Check if the blood request is active"""
        return self.status == 'active'

    def is_pending(self):
        """Check if the blood request is pending"""
        return self.status == 'pending'

    def is_completed(self):
        """Check if the blood request is completed"""
        return self.status == 'completed'

    def is_cancelled(self):
        """Check if the blood request is cancelled"""
        return self.status == 'cancelled'

    def activate(self):
        """Activate the blood request"""
        self.status = 'active'
        self.save()

    def complete(self):
        """Mark the blood request as completed"""
        self.status = 'completed'
        self.to_date = date.today()
        self.save()

    def cancel(self):
        """Cancel the blood request"""
        self.status = 'cancelled'
        self.to_date = date.today()
        self.save()

    def get_responses_count(self):
        """Get the number of responses for this request"""
        return len(self.responses) if self.responses else 0

    def get_accepted_responses(self):
        """Get accepted responses for this request"""
        return [r for r in self.responses if r.response_status == 'accepted']

class BloodRequestResponse(BaseModel):
    __tablename__ = 'blood_requests_responses'

    blood_requests_response_id = db.Column(db.Integer, primary_key=True)
    blood_request_id = db.Column(db.Integer, db.ForeignKey('blood_requests.blood_request_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    response_status = db.Column(db.String(20), nullable=False)  # accepted, declined, pending
    message = db.Column(db.Text, nullable=True)
    from_date = db.Column(db.Date, nullable=False, default=date.today)
    responded_date = db.Column(db.Date, nullable=True)
    to_date = db.Column(db.Date, nullable=True)
    scheduled_datetime = db.Column(db.DateTime, nullable=True)

    # Relationships
    blood_request = db.relationship('BloodRequest', back_populates='responses')
    responder = db.relationship('User')

    def __init__(self, blood_request_id, user_id, response_status, from_date=None, scheduled_datetime=None, **kwargs):
        self.blood_request_id = blood_request_id
        self.user_id = user_id
        self.response_status = response_status
        self.from_date = from_date if from_date else date.today()
        self.scheduled_datetime = scheduled_datetime
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            'blood_requests_response_id': self.blood_requests_response_id,
            'blood_request_id': self.blood_request_id,
            'user_id': self.user_id,
            'response_status': self.response_status,
            'message': self.message,
            'from_date': self.from_date.isoformat() if self.from_date else None,
            'responded_date': self.responded_date.isoformat() if self.responded_date else None,
            'to_date': self.to_date.isoformat() if self.to_date else None,
            'scheduled_datetime': self.scheduled_datetime.isoformat() if self.scheduled_datetime else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'responder': self.responder.to_dict() if self.responder else None,
        }

    def accept(self, scheduled_datetime=None, message=None):
        """Accept the blood request response"""
        self.response_status = 'accepted'
        self.responded_date = date.today()
        self.scheduled_datetime = scheduled_datetime
        if message:
            self.message = message
        self.save()

    def decline(self, message=None):
        """Decline the blood request response"""
        self.response_status = 'declined'
        self.responded_date = date.today()
        if message:
            self.message = message
        self.save()

    def is_accepted(self):
        """Check if the response is accepted"""
        return self.response_status == 'accepted'

    def is_declined(self):
        """Check if the response is declined"""
        return self.response_status == 'declined'

    def is_pending(self):
        """Check if the response is pending"""
        return self.response_status == 'pending' 