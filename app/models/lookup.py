from datetime import date
from . import db, BaseModel

class LookupRole(BaseModel):
    __tablename__ = 'lookup_roles'

    lookup_role_id = db.Column(db.Integer, primary_key=True)
    lookup_role_name = db.Column(db.Text, nullable=False, unique=True)
    from_date = db.Column(db.Date, nullable=False, default=date.today)
    to_date = db.Column(db.Date, nullable=True)

    def __init__(self, lookup_role_name, from_date=None, to_date=None):
        self.lookup_role_name = lookup_role_name
        self.from_date = from_date if from_date else date.today()
        self.to_date = to_date

    def to_dict(self):
        return {
            'lookup_role_id': self.lookup_role_id,
            'lookup_role_name': self.lookup_role_name,
            'from_date': self.from_date.isoformat() if self.from_date else None,
            'to_date': self.to_date.isoformat() if self.to_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class LookupBloodGroup(BaseModel):
    __tablename__ = 'lookup_blood_groups'

    blood_group_id = db.Column(db.Integer, primary_key=True)
    blood_group_name = db.Column(db.Text, nullable=False, unique=True)
    from_date = db.Column(db.Date, nullable=False, default=date.today)
    to_date = db.Column(db.Date, nullable=True)

    # Relationships
    hospital_availabilities = db.relationship('HospitalBloodAvailability', back_populates='blood_group')

    def __init__(self, blood_group_name, from_date=None, to_date=None):
        self.blood_group_name = blood_group_name
        self.from_date = from_date if from_date else date.today()
        self.to_date = to_date

    def to_dict(self):
        return {
            'blood_group_id': self.blood_group_id,
            'blood_group_name': self.blood_group_name,
            'from_date': self.from_date.isoformat() if self.from_date else None,
            'to_date': self.to_date.isoformat() if self.to_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        } 