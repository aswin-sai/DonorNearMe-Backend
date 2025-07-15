from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, BaseModel

class User(BaseModel):
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
    
    # Relationships
    role = db.relationship('LookupRole', backref='users')
    admin_lineages = db.relationship('UserHospitalAdminLineage', back_populates='user')
    blood_requests = db.relationship('BloodRequest', back_populates='requester')
    device_tokens = db.relationship('DeviceToken', back_populates='user')

    def __init__(self, user_name, password, from_date=None, to_date=None, **kwargs):
        self.user_name = user_name
        self.set_password(password)
        self.from_date = from_date if from_date else date.today()
        self.to_date = to_date

        self.blood_group = kwargs.get('blood_group')
        self.address = kwargs.get('address')
        self.pincode = kwargs.get('pincode')
        self.user_email = kwargs.get('user_email')
        self.user_phone_number = kwargs.get('user_phone_number')
        self.user_role_id = kwargs.get('user_role_id')

    def set_password(self, password):
        """Hash and set password"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hashed password"""
        return check_password_hash(self.password, password)

    def to_dict(self):
        """Convert user to dictionary excluding sensitive data"""
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_email': self.user_email,
            'user_phone_number': self.user_phone_number,
            'user_role_id': self.user_role_id,
            'blood_group': self.blood_group,
            'address': self.address,
            'pincode': self.pincode,
            'from_date': self.from_date.isoformat() if self.from_date else None,
            'to_date': self.to_date.isoformat() if self.to_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def is_hospital_admin(self):
        """Check if user is a hospital admin"""
        return self.user_role_id == 2  # Assuming 2 is hospital admin role

    def is_super_admin(self):
        """Check if user is a super admin"""
        return self.user_role_id == 1  # Assuming 1 is super admin role

    def is_donor(self):
        """Check if user is a donor"""
        return self.user_role_id == 3  # Assuming 3 is donor role

class UserHospitalAdminLineage(BaseModel):
    __tablename__ = 'user_hospital_admin_lineage'

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.hospital_id'), primary_key=True)
    from_date = db.Column(db.Date, nullable=False, default=date.today)
    to_date = db.Column(db.Date, nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='admin_lineages')
    hospital = db.relationship('Hospital', back_populates='admin_lineages')

    def __init__(self, user_id, hospital_id, from_date=None, to_date=None):
        self.user_id = user_id
        self.hospital_id = hospital_id
        self.from_date = from_date if from_date else date.today()
        self.to_date = to_date

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'hospital_id': self.hospital_id,
            'from_date': self.from_date.isoformat() if self.from_date else None,
            'to_date': self.to_date.isoformat() if self.to_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        } 