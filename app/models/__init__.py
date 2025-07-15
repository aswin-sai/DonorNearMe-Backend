from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class BaseModel(db.Model):
    """Base model with common fields and methods"""
    __abstract__ = True
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def save(self):
        """Save the model to database"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self):
        """Delete the model from database"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Import all models
from .user import User, UserHospitalAdminLineage
from .hospital import Hospital, HospitalBloodAvailability
from .blood_request import BloodRequest, BloodRequestResponse
from .lookup import LookupRole, LookupBloodGroup
from .device_token import DeviceToken 