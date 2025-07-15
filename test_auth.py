#!/usr/bin/env python3
"""
Simple authentication test script
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_auth():
    """Test authentication and blood requests"""
    
    print("Testing Authentication and Blood Requests")
    print("=" * 50)
    
    # Test login
    print("1. Testing login...")
    login_data = {
        "emailaddress": "test@example.com",
        "password": "testpassword123"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login Status: {login_response.status_code}")
    print(f"Login Response: {login_response.text}")
    
    if login_response.status_code == 200:
        response_data = login_response.json()
        token = response_data.get('access_token') or response_data.get('token')
        
        if token:
            print(f"✓ Token received: {token[:20]}...")
            
            # Test blood requests with token
            headers = {'Authorization': f'Bearer {token}'}
            
            print("\n2. Testing blood requests with token...")
            blood_response = requests.get(f"{BASE_URL}/blood/requests", headers=headers)
            print(f"Blood Requests Status: {blood_response.status_code}")
            print(f"Blood Requests Response: {blood_response.text}")
            
            if blood_response.status_code == 200:
                print("✓ Blood requests endpoint working!")
            else:
                print("✗ Blood requests endpoint failed")
        else:
            print("✗ No token in response")
    else:
        print("✗ Login failed")

if __name__ == "__main__":
    test_auth() 