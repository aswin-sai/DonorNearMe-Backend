#!/usr/bin/env python3
"""
Test script for the refactored Donor Near Me application
"""

import requests
import json
from datetime import date

# Configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def test_health_check():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Health check: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server first.")
        return False

def test_user_registration():
    """Test user registration"""
    url = f"{BASE_URL}/auth/register"
    data = {
        "user_name": "Test User",
        "user_email": TEST_EMAIL,
        "user_phone_number": "+1234567890",
        "password": TEST_PASSWORD,
        "blood_group": "O+",
        "address": "123 Test St",
        "pincode": "12345",
        "user_role_id": 3  # Donor
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"✅ User registration: {response.status_code}")
        if response.status_code == 201:
            return response.json().get('data', {}).get('user_id')
        return None
    except Exception as e:
        print(f"❌ User registration failed: {e}")
        return None

def test_user_login():
    """Test user login"""
    url = f"{BASE_URL}/auth/login"
    data = {
        "user_email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"✅ User login: {response.status_code}")
        if response.status_code == 200:
            return response.json().get('data', {}).get('access_token')
        return None
    except Exception as e:
        print(f"❌ User login failed: {e}")
        return None

def test_hospital_listing(token):
    """Test hospital listing"""
    url = f"{BASE_URL}/hospital"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"✅ Hospital listing: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Hospital listing failed: {e}")
        return False

def test_blood_request_creation(token):
    """Test blood request creation"""
    url = f"{BASE_URL}/blood/request"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    data = {
        "hospital_id": 1,
        "blood_group_type": 1,
        "no_of_units": 2,
        "patient_name": "Test Patient",
        "required_by_date": date.today().isoformat(),
        "description": "Test blood request"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"✅ Blood request creation: {response.status_code}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ Blood request creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Refactored Donor Near Me Application")
    print("=" * 50)
    
    # Test server health
    if not test_health_check():
        return
    
    # Test user registration
    user_id = test_user_registration()
    
    # Test user login
    token = test_user_login()
    
    # Test authenticated endpoints
    if token:
        test_hospital_listing(token)
        test_blood_request_creation(token)
    
    print("\n🎉 Testing completed!")

if __name__ == "__main__":
    main() 