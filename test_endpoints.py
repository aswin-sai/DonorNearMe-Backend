#!/usr/bin/env python3
"""
Comprehensive test script for blood requests and hospital endpoints
"""

import requests
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_all_endpoints():
    """Test all blood request and hospital endpoints"""
    
    print("Testing Blood Request and Hospital Endpoints")
    print("=" * 60)
    
    # Test data
    test_user_credentials = {
        "emailaddress": "test@example.com",
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
        response_data = login_response.json()
        token = response_data.get('access_token') or response_data.get('token')
        headers = {'Authorization': f'Bearer {token}'}
        print("✓ Login successful")
        print(f"  Token: {token[:20]}...")
    else:
        print(f"✗ Login failed: {login_response.status_code} - {login_response.text}")
        return
    
    # Step 2: Test hospital endpoints
    print("\n2. Testing hospital endpoints...")
    
    # Get hospital list
    print("  2.1. Testing GET /hospital/list...")
    hospital_list_response = requests.get(f"{BASE_URL}/hospital/list")
    if hospital_list_response.status_code == 200:
        hospitals = hospital_list_response.json()
        print(f"  ✓ Found {len(hospitals)} hospitals")
        for hospital in hospitals[:2]:  # Show first 2
            print(f"    - {hospital['hospital_name']} (ID: {hospital['hospital_id']})")
    else:
        print(f"  ✗ Failed to get hospitals: {hospital_list_response.status_code}")
    
    # Get specific hospital
    if hospitals:
        hospital_id = hospitals[0]['hospital_id']
        print(f"  2.2. Testing GET /hospital/{hospital_id}...")
        hospital_detail_response = requests.get(f"{BASE_URL}/hospital/{hospital_id}")
        if hospital_detail_response.status_code == 200:
            hospital_detail = hospital_detail_response.json()
            print(f"  ✓ Hospital details retrieved: {hospital_detail['hospital_name']}")
        else:
            print(f"  ✗ Failed to get hospital details: {hospital_detail_response.status_code}")
    
    # Step 3: Test blood groups endpoint
    print("\n3. Testing blood groups endpoint...")
    blood_groups_response = requests.get(f"{BASE_URL}/blood/blood-groups")
    if blood_groups_response.status_code == 200:
        blood_groups = blood_groups_response.json()
        print(f"✓ Found {len(blood_groups)} blood groups")
        for bg in blood_groups:
            print(f"  - {bg['blood_group_name']} (ID: {bg['blood_group_id']})")
    else:
        print(f"✗ Failed to get blood groups: {blood_groups_response.status_code}")
    
    # Step 4: Create blood request
    print("\n4. Testing create blood request...")
    create_response = requests.post(
        f"{BASE_URL}/blood/request", 
        json=test_blood_request,
        headers=headers
    )
    
    if create_response.status_code == 201:
        request_data = create_response.json()
        request_id = request_data.get('blood_request_id')
        print(f"✓ Blood request created successfully (ID: {request_id})")
        print(f"  Response: {request_data}")
    else:
        print(f"✗ Failed to create blood request: {create_response.status_code}")
        print(f"  Response: {create_response.text}")
        return
    
    # Step 5: Get all blood requests
    print("\n5. Testing get all blood requests...")
    all_requests_response = requests.get(f"{BASE_URL}/blood/requests", headers=headers)
    if all_requests_response.status_code == 200:
        requests_list = all_requests_response.json()
        print(f"✓ Found {len(requests_list)} blood requests")
        for req in requests_list[:3]:  # Show first 3
            print(f"  - {req['patient_name']} ({req['blood_group_name']}) - {req['status']}")
    else:
        print(f"✗ Failed to get blood requests: {all_requests_response.status_code}")
    
    # Step 6: Get specific blood request
    print(f"\n6. Testing get specific blood request (ID: {request_id})...")
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
    
    # Step 8: Respond to blood request
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
    
    # Step 9: Get my blood requests
    print("\n9. Testing get my blood requests...")
    my_requests_response = requests.get(f"{BASE_URL}/blood/my-requests", headers=headers)
    if my_requests_response.status_code == 200:
        my_requests = my_requests_response.json()
        print(f"✓ Found {len(my_requests)} of my blood requests")
        for req in my_requests:
            print(f"  - {req['patient_name']} ({req['blood_group_name']}) - {req['status']}")
    else:
        print(f"✗ Failed to get my blood requests: {my_requests_response.status_code}")
    
    # Step 10: Test hospital search
    print("\n10. Testing hospital search...")
    search_response = requests.get(f"{BASE_URL}/hospital/search?has_blood_bank=true")
    if search_response.status_code == 200:
        search_results = search_response.json()
        print(f"✓ Found {len(search_results)} hospitals with blood banks")
        for hospital in search_results[:2]:
            print(f"  - {hospital['hospital_name']} (Blood Bank: {hospital['has_blood_bank']})")
    else:
        print(f"✗ Failed to search hospitals: {search_response.status_code}")
    
    print("\n" + "=" * 60)
    print("All endpoint tests completed!")

if __name__ == "__main__":
    test_all_endpoints() 