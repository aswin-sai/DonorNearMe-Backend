from app import create_app, db
from models import User, Hospital, BloodRequest, LookupRole, LookupBloodGroup, DeviceToken, UserHospitalAdminLineage, BloodRequestResponse, HospitalBloodAvailability
from datetime import date

def init_db():
    """Initialize database with tables and seed data"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Seed lookup data
        seed_lookup_data()
        
        print("Database initialized successfully!")

def seed_lookup_data():
    """Seed lookup tables with initial data"""
    # Seed roles
    roles = [
        {'lookup_role_name': 'Super Admin'},
        {'lookup_role_name': 'Hospital Admin'},
        {'lookup_role_name': 'Donor'}
    ]
    
    for role_data in roles:
        role = LookupRole.query.filter_by(lookup_role_name=role_data['lookup_role_name']).first()
        if not role:
            role = LookupRole(**role_data)
            role.save()
            print(f"Created role: {role_data['lookup_role_name']}")
    
    # Seed blood groups
    blood_groups = [
        {'blood_group_name': 'A+'},
        {'blood_group_name': 'A-'},
        {'blood_group_name': 'B+'},
        {'blood_group_name': 'B-'},
        {'blood_group_name': 'AB+'},
        {'blood_group_name': 'AB-'},
        {'blood_group_name': 'O+'},
        {'blood_group_name': 'O-'}
    ]
    
    for bg_data in blood_groups:
        bg = LookupBloodGroup.query.filter_by(blood_group_name=bg_data['blood_group_name']).first()
        if not bg:
            bg = LookupBloodGroup(**bg_data)
            bg.save()
            print(f"Created blood group: {bg_data['blood_group_name']}")

if __name__ == '__main__':
    init_db() 