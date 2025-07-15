# Blood Request API Documentation

## Overview
The Blood Request API provides endpoints for managing blood donation requests, responses, and related functionality in the Donor Near Me application.

## Authentication
All endpoints (except `/blood/blood-groups`) require JWT authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. Create Blood Request
**POST** `/blood/request`

Creates a new blood donation request.

**Request Body:**
```json
{
  "hospital_id": 1,
  "blood_group_type": 1,
  "no_of_units": 2,
  "patient_name": "John Doe",
  "required_by_date": "2024-01-15",
  "patient_contact_email": "john.doe@example.com",
  "patient_contact_phone_number": "+1234567890",
  "description": "Emergency blood requirement for surgery"
}
```

**Required Fields:**
- `hospital_id`: ID of the hospital
- `blood_group_type`: ID of the blood group
- `no_of_units`: Number of blood units required
- `patient_name`: Name of the patient
- `required_by_date`: Date when blood is required (YYYY-MM-DD format)

**Optional Fields:**
- `patient_contact_email`: Patient's contact email
- `patient_contact_phone_number`: Patient's contact phone number
- `description`: Additional description

**Response (201):**
```json
{
  "message": "Blood request created successfully",
  "blood_request_id": 123
}
```

**Error Responses:**
- `400`: Missing required fields or invalid data
- `404`: Hospital or blood group not found
- `500`: Server error

---

### 2. Get All Blood Requests
**GET** `/blood/requests`

Retrieves all blood requests with optional filtering.

**Query Parameters:**
- `status`: Filter by request status (pending, accepted, cancelled, completed)
- `blood_group_id`: Filter by blood group ID
- `hospital_id`: Filter by hospital ID
- `user_id`: Filter by user ID

**Example:**
```
GET /blood/requests?status=pending&blood_group_id=1
```

**Response (200):**
```json
[
  {
    "blood_request_id": 123,
    "user_id": 1,
    "user_name": "John Doe",
    "hospital_id": 1,
    "hospital_name": "City General Hospital",
    "blood_group_type": 1,
    "blood_group_name": "A+",
    "no_of_units": 2,
    "patient_name": "Jane Smith",
    "patient_contact_email": "jane@example.com",
    "patient_contact_phone_number": "+1234567890",
    "required_by_date": "2024-01-15",
    "description": "Emergency requirement",
    "status": "pending",
    "from_date": "2024-01-08",
    "to_date": null,
    "created_at": "2024-01-08T10:30:00",
    "updated_at": "2024-01-08T10:30:00"
  }
]
```

---

### 3. Get Specific Blood Request
**GET** `/blood/request/{request_id}`

Retrieves details of a specific blood request including responses.

**Response (200):**
```json
{
  "blood_request_id": 123,
  "user_id": 1,
  "user_name": "John Doe",
  "hospital_id": 1,
  "hospital_name": "City General Hospital",
  "blood_group_type": 1,
  "blood_group_name": "A+",
  "no_of_units": 2,
  "patient_name": "Jane Smith",
  "patient_contact_email": "jane@example.com",
  "patient_contact_phone_number": "+1234567890",
  "required_by_date": "2024-01-15",
  "description": "Emergency requirement",
  "status": "pending",
  "from_date": "2024-01-08",
  "to_date": null,
  "created_at": "2024-01-08T10:30:00",
  "updated_at": "2024-01-08T10:30:00",
  "responses": [
    {
      "blood_requests_response_id": 1,
      "user_id": 2,
      "user_name": "Donor User",
      "response_status": "accepted",
      "message": "I can donate blood",
      "from_date": "2024-01-08",
      "responded_date": "2024-01-08",
      "to_date": null,
      "created_at": "2024-01-08T11:00:00"
    }
  ]
}
```

**Error Responses:**
- `404`: Blood request not found

---

### 4. Update Blood Request
**PUT** `/blood/request/{request_id}`

Updates an existing blood request. Only the request creator can update it.

**Request Body:**
```json
{
  "no_of_units": 3,
  "patient_name": "Jane Smith Updated",
  "patient_contact_email": "jane.updated@example.com",
  "patient_contact_phone_number": "+1234567891",
  "required_by_date": "2024-01-20",
  "description": "Updated description",
  "status": "pending"
}
```

**Updatable Fields:**
- `no_of_units`
- `patient_name`
- `patient_contact_email`
- `patient_contact_phone_number`
- `required_by_date`
- `description`
- `status`

**Response (200):**
```json
{
  "message": "Blood request updated successfully"
}
```

**Error Responses:**
- `403`: Unauthorized to update this request
- `404`: Blood request not found
- `400`: Invalid data format

---

### 5. Delete Blood Request
**DELETE** `/blood/request/{request_id}`

Soft deletes a blood request by setting it as cancelled. Only the request creator can delete it.

**Response (200):**
```json
{
  "message": "Blood request cancelled successfully"
}
```

**Error Responses:**
- `403`: Unauthorized to delete this request
- `404`: Blood request not found

---

### 6. Respond to Blood Request
**POST** `/blood/request/{request_id}/respond`

Allows users to respond to blood requests (accept/decline).

**Request Body:**
```json
{
  "response_status": "accepted",
  "message": "I can donate blood. Please contact me."
}
```

**Response Status Values:**
- `accepted`: User can donate blood
- `declined`: User cannot donate blood

**Response (201):**
```json
{
  "message": "Response submitted successfully",
  "response_id": 1
}
```

**Error Responses:**
- `400`: Missing response_status, cannot respond to own request, or already responded
- `404`: Blood request not found

---

### 7. Get My Blood Requests
**GET** `/blood/my-requests`

Retrieves blood requests created by the current user.

**Response (200):**
```json
[
  {
    "blood_request_id": 123,
    "hospital_name": "City General Hospital",
    "blood_group_name": "A+",
    "no_of_units": 2,
    "patient_name": "Jane Smith",
    "required_by_date": "2024-01-15",
    "status": "pending",
    "created_at": "2024-01-08T10:30:00"
  }
]
```

---

### 8. Get Blood Groups
**GET** `/blood/blood-groups`

Retrieves all available blood groups. No authentication required.

**Response (200):**
```json
[
  {
    "blood_group_id": 1,
    "blood_group_name": "A+"
  },
  {
    "blood_group_id": 2,
    "blood_group_name": "A-"
  },
  {
    "blood_group_id": 3,
    "blood_group_name": "B+"
  }
]
```

## Status Values

### Blood Request Status
- `pending`: Request is waiting for responses
- `accepted`: Request has been accepted by a donor
- `cancelled`: Request has been cancelled
- `completed`: Blood donation has been completed

### Response Status
- `accepted`: Donor can provide blood
- `declined`: Donor cannot provide blood

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error message description"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (missing or invalid JWT)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `500`: Internal Server Error

## Example Usage

### Complete Workflow

1. **Login to get JWT token:**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_email": "user@example.com", "password": "password123"}'
```

2. **Create a blood request:**
```bash
curl -X POST http://localhost:5000/blood/request \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "hospital_id": 1,
    "blood_group_type": 1,
    "no_of_units": 2,
    "patient_name": "John Doe",
    "required_by_date": "2024-01-15",
    "description": "Emergency requirement"
  }'
```

3. **Get all blood requests:**
```bash
curl -X GET http://localhost:5000/blood/requests \
  -H "Authorization: Bearer <your_jwt_token>"
```

4. **Respond to a blood request:**
```bash
curl -X POST http://localhost:5000/blood/request/123/respond \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "response_status": "accepted",
    "message": "I can donate blood"
  }'
``` 