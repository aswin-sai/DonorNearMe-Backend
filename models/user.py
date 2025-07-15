from datetime import date
from db import db

# ---------------------
# User Model
# ---------------------
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.Text, nullable=False)
    blood_group = db.Column(db.String(5), nullable=True)
    address = db.Column(db.Text, nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    user_email = db.Column(db.Text, unique=True, nullable=False)
    user_phone_number = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    user_role_id = db.Column(db.Integer, db.ForeignKey('lookup_roles.lookup_role_id'), nullable=False)
    from_date = db.Column(db.Date, nullable=False, default=date.today)
    to_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, user_name, password, from_date=None, to_date=None, **kwargs):
        self.user_name = user_name
        self.password = password
        self.from_date = from_date if from_date else date.today()
        self.to_date = to_date

        self.blood_group = kwargs.get('blood_group')
        self.address = kwargs.get('address')
        self.pincode = kwargs.get('pincode')
        self.user_email = kwargs.get('user_email')
        self.user_phone_number = kwargs.get('user_phone_number')
        self.user_role_id = kwargs.get('user_role_id')

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_email': self.user_email,
            'user_phone_number': self.user_phone_number,
            'user_role_id': self.user_role_id,
        }

# ---------------------
# UserHospitalAdminLineage Model
# ---------------------
class UserHospitalAdminLineage(db.Model):
    __tablename__ = 'user_hospital_admin_lineage'

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.hospital_id'), primary_key=True)
    from_date = db.Column(db.Date, nullable=False, default=date.today)
    to_date = db.Column(db.Date, nullable=True)

    user = db.relationship('User', backref='admin_lineage')
    hospital = db.relationship('Hospital', backref='admin_lineages')

    def __init__(self, user_id, hospital_id, from_date=None, to_date=None):
        self.user_id = user_id
        self.hospital_id = hospital_id
        self.from_date = from_date if from_date else date.today()
        self.to_date = to_date

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'hospital_id': self.hospital_id,
            'from_date': self.from_date,
            'to_date': self.to_date,
        }
