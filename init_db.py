#!/usr/bin/env python3
"""
Database initialization script for Donor Near Me application
"""

from app import create_app
from db import db
from models import *
from datetime import date
import bcrypt

def init_database():
    """Initialize the database with tables and seed data"""
    
    app = create_app()
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully")
        
        # Seed lookup data
        print("\nSeeding lookup data...")
        seed_lookup_data()
        
        # Seed test data
        print("\nSeeding test data...")
        seed_test_data()
        
        print("\n✓ Database initialization completed successfully!")

def seed_lookup_data():
    """Seed lookup tables with initial data"""
    
    # Blood Groups
    blood_groups = [
        "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"
    ]
    
    for bg_name in blood_groups:
        existing = LookupBloodGroup.query.filter_by(blood_group_name=bg_name).first()
        if not existing:
            blood_group = LookupBloodGroup(
                blood_group_name=bg_name,
                from_date=date.today()
            )
            db.session.add(blood_group)
    
    # User Roles
    roles = [
        "admin", "user", "hospital_admin", "donor"
    ]
    
    for role_name in roles:
        existing = LookupRole.query.filter_by(lookup_role_name=role_name).first()
        if not existing:
            role = LookupRole(
                lookup_role_name=role_name,
                from_date=date.today()
            )
            db.session.add(role)
    
    db.session.commit()
    print("✓ Lookup data seeded")

def seed_test_data():
    """Seed test data for development"""
    
    # Create test hospitals
    hospitals = [
        {
            "hospital_name": "City General Hospital",
            "hospital_address": "123 Main Street, City Center",
            "hospital_address_lat": 12.9716,
            "hospital_address_long": 77.5946,
            "hospital_contact_number": "+91-80-12345678",
            "hospital_email_id": "info@citygeneral.com",
            "hospital_contact_person": "Dr. Smith",
            "hospital_pincode": "560001",
            "hospital_type": "General",
            "has_blood_bank": True
        },
        {
            "hospital_name": "Metro Medical Center",
            "hospital_address": "456 Park Avenue, Downtown",
            "hospital_address_lat": 12.9789,
            "hospital_address_long": 77.5917,
            "hospital_contact_number": "+91-80-87654321",
            "hospital_email_id": "contact@metromedical.com",
            "hospital_contact_person": "Dr. Johnson",
            "hospital_pincode": "560002",
            "hospital_type": "Specialty",
            "has_blood_bank": True
        }
    ]
    
    for hospital_data in hospitals:
        existing = Hospital.query.filter_by(hospital_name=hospital_data["hospital_name"]).first()
        if not existing:
            hospital = Hospital(
                hospital_name=hospital_data["hospital_name"],
                from_date=date.today(),
                **{k: v for k, v in hospital_data.items() if k != "hospital_name"}
            )
            db.session.add(hospital)
    
    # Create test users
    users = [
        {
            "user_name": "Test User",
            "user_email": "test@example.com",
            "user_phone_number": "+91-9876543210",
            "password": "testpassword123",
            "blood_group": "A+",
            "address": "Test Address, Test City",
            "pincode": "560001",
            "user_role_id": 2  # user role
        },
        {
            "user_name": "Donor User",
            "user_email": "donor@example.com",
            "user_phone_number": "+91-9876543211",
            "password": "donorpassword123",
            "blood_group": "O+",
            "address": "Donor Address, Donor City",
            "pincode": "560002",
            "user_role_id": 2  # user role
        },
        {
            "user_name": "Admin User",
            "user_email": "admin@example.com",
            "user_phone_number": "+91-9876543212",
            "password": "adminpassword123",
            "blood_group": "B+",
            "address": "Admin Address, Admin City",
            "pincode": "560003",
            "user_role_id": 1  # admin role
        },
        {
            "user_name": "Seeded Hospital Admin",
            "user_email": "hospitaladmin@example.com",
            "user_phone_number": "+91-9999999999",
            "password": "Hospital123!",
            "blood_group": "A+",
            "address": "Seeded Admin Address, City",
            "pincode": "560005",
            "user_role_id": 1  # hospital_admin role
        }
    ]
    
    for user_data in users:
        existing = User.query.filter_by(user_email=user_data["user_email"]).first()
        if not existing:
            # Hash password
            password_hash = bcrypt.hashpw(
                user_data["password"].encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            user = User(
                user_name=user_data["user_name"],
                password=password_hash,
                user_email=user_data["user_email"],
                user_phone_number=user_data["user_phone_number"],
                blood_group=user_data["blood_group"],
                address=user_data["address"],
                pincode=user_data["pincode"],
                user_role_id=user_data["user_role_id"]
            )
            db.session.add(user)
    
    db.session.commit()
    print("✓ Test data seeded")

if __name__ == "__main__":
    init_database() 