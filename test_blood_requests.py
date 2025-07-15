#!/usr/bin/env python3
"""
Test script for blood request functionality
"""

import requests
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_blood_requests():
    """Test blood request endpoints"""
    
    print("Testing Blood Request Functionality")
    print("=" * 50)
    
    # Test data
    test_user_credentials = {
        "user_email": "test@example.com",
        "password": "testpassword123"
    }
    
    test_blood_request = {
        "hospital_id": 1,
        "blood_group_type": 1,
        "no_of_units": 2,
        "patient_name": "John Doe",
        "required_by_date": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
        "patient_contact_email": "john.doe@example.com",
        "patient_contact_phone_number": "+1234567890",
        "description": "Emergency blood requirement for surgery"
    }
    
    # Step 1: Login to get JWT token
    print("1. Testing login...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json=test_user_credentials)
    
    if login_response.status_code == 200:
        token = login_response.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        print("✓ Login successful")
    else:
        print(f"✗ Login failed: {login_response.status_code} - {login_response.text}")
        return
    
    # Step 2: Get blood groups
    print("\n2. Testing get blood groups...")
    blood_groups_response = requests.get(f"{BASE_URL}/blood/blood-groups")
    if blood_groups_response.status_code == 200:
        blood_groups = blood_groups_response.json()
        print(f"✓ Found {len(blood_groups)} blood groups")
        for bg in blood_groups:
            print(f"  - {bg['blood_group_name']} (ID: {bg['blood_group_id']})")
    else:
        print(f"✗ Failed to get blood groups: {blood_groups_response.status_code}")
    
    # Step 3: Create blood request
    print("\n3. Testing create blood request...")
    create_response = requests.post(
        f"{BASE_URL}/blood/request", 
        json=test_blood_request,
        headers=headers
    )
    
    if create_response.status_code == 201:
        request_data = create_response.json()
        request_id = request_data.get('blood_request_id')
        print(f"✓ Blood request created successfully (ID: {request_id})")
    else:
        print(f"✗ Failed to create blood request: {create_response.status_code} - {create_response.text}")
        return
    
    # Step 4: Get all blood requests
    print("\n4. Testing get all blood requests...")
    all_requests_response = requests.get(f"{BASE_URL}/blood/requests", headers=headers)
    if all_requests_response.status_code == 200:
        requests_list = all_requests_response.json()
        print(f"✓ Found {len(requests_list)} blood requests")
        for req in requests_list[:3]:  # Show first 3
            print(f"  - {req['patient_name']} ({req['blood_group_name']}) - {req['status']}")
    else:
        print(f"✗ Failed to get blood requests: {all_requests_response.status_code}")
    
    # Step 5: Get specific blood request
    print(f"\n5. Testing get specific blood request (ID: {request_id})...")
    specific_request_response = requests.get(f"{BASE_URL}/blood/request/{request_id}", headers=headers)
    if specific_request_response.status_code == 200:
        request_details = specific_request_response.json()
        print(f"✓ Blood request details retrieved")
        print(f"  - Patient: {request_details['patient_name']}")
        print(f"  - Blood Group: {request_details['blood_group_name']}")
        print(f"  - Status: {request_details['status']}")
        print(f"  - Responses: {len(request_details['responses'])}")
    else:
        print(f"✗ Failed to get specific blood request: {specific_request_response.status_code}")
    
    # Step 6: Get my blood requests
    print("\n6. Testing get my blood requests...")
    my_requests_response = requests.get(f"{BASE_URL}/blood/my-requests", headers=headers)
    if my_requests_response.status_code == 200:
        my_requests = my_requests_response.json()
        print(f"✓ Found {len(my_requests)} of my blood requests")
        for req in my_requests:
            print(f"  - {req['patient_name']} ({req['blood_group_name']}) - {req['status']}")
    else:
        print(f"✗ Failed to get my blood requests: {my_requests_response.status_code}")
    
    # Step 7: Update blood request
    print(f"\n7. Testing update blood request (ID: {request_id})...")
    update_data = {
        "description": "Updated description - Urgent requirement",
        "no_of_units": 3
    }
    update_response = requests.put(
        f"{BASE_URL}/blood/request/{request_id}",
        json=update_data,
        headers=headers
    )
    if update_response.status_code == 200:
        print("✓ Blood request updated successfully")
    else:
        print(f"✗ Failed to update blood request: {update_response.status_code} - {update_response.text}")
    
    # Step 8: Respond to blood request (simulate another user)
    print(f"\n8. Testing respond to blood request (ID: {request_id})...")
    response_data = {
        "response_status": "accepted",
        "message": "I can donate blood. Please contact me."
    }
    respond_response = requests.post(
        f"{BASE_URL}/blood/request/{request_id}/respond",
        json=response_data,
        headers=headers
    )
    if respond_response.status_code == 201:
        response_info = respond_response.json()
        print(f"✓ Response submitted successfully (ID: {response_info.get('response_id')})")
    else:
        print(f"✗ Failed to respond to blood request: {respond_response.status_code} - {respond_response.text}")
    
    print("\n" + "=" * 50)
    print("Blood request functionality test completed!")

if __name__ == "__main__":
    test_blood_requests() 