from db import db
from datetime import datetime

class Hospital(db.Model):
    __tablename__ = 'hospitals'
    hospital_id = db.Column(db.Integer, primary_key=True)
    hospital_name = db.Column(db.String(120), nullable=False)
    hospital_address = db.Column(db.String(255), nullable=True)
    hospital_address_lat = db.Column(db.Float, nullable=True)
    hospital_address_long = db.Column(db.Float, nullable=True)
    hospital_gmap_link = db.Column(db.String(500), nullable=True)
    has_blood_bank = db.Column(db.Boolean, default=False)
    hospital_contact_number = db.Column(db.String(20), nullable=True)
    hospital_email_id = db.Column(db.String(120), nullable=True)
    hospital_contact_person = db.Column(db.String(120), nullable=True)
    hospital_pincode = db.Column(db.String(10), nullable=True)
    hospital_type = db.Column(db.String(50), nullable=True)
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, hospital_name, **kwargs):
        self.hospital_name = hospital_name
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            'hospital_id': self.hospital_id,
            'hospital_name': self.hospital_name,
            'hospital_address': self.hospital_address,
            'hospital_contact_number': self.hospital_contact_number,
            'hospital_email_id': self.hospital_email_id,
        }


class HospitalBloodAvailability(db.Model):
    __tablename__ = 'hospital_blood_availability'

    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.hospital_id'), primary_key=True)
    blood_group_id = db.Column(db.Integer, db.ForeignKey('lookup_blood_groups.blood_group_id'), primary_key=True)
    no_of_units = db.Column(db.Integer, nullable=False)
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=True)

    hospital = db.relationship('Hospital', backref='blood_availabilities')
    blood_group = db.relationship('LookupBloodGroup', backref='hospital_availabilities')

    def __init__(self, hospital_id, blood_group_id, no_of_units, from_date, to_date=None):
        self.hospital_id = hospital_id
        self.blood_group_id = blood_group_id
        self.no_of_units = no_of_units
        self.from_date = from_date
        self.to_date = to_date