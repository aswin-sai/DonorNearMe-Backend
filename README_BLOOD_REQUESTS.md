# Blood Request Functionality - Donor Near Me

## Overview
This module provides comprehensive blood request management functionality for the Donor Near Me application. Users can create, view, update, and respond to blood donation requests.

## Features

### Core Functionality
- ✅ Create blood donation requests
- ✅ View all blood requests with filtering
- ✅ Get specific blood request details
- ✅ Update blood requests
- ✅ Delete/cancel blood requests
- ✅ Respond to blood requests (accept/decline)
- ✅ View user's own blood requests
- ✅ Get available blood groups
- ✅ JWT authentication integration
- ✅ Comprehensive error handling
- ✅ Database relationships and constraints

### API Endpoints
1. `POST /blood/request` - Create new blood request
2. `GET /blood/requests` - Get all blood requests (with filters)
3. `GET /blood/request/{id}` - Get specific blood request
4. `PUT /blood/request/{id}` - Update blood request
5. `DELETE /blood/request/{id}` - Cancel blood request
6. `POST /blood/request/{id}/respond` - Respond to blood request
7. `GET /blood/my-requests` - Get user's own requests
8. `GET /blood/blood-groups` - Get available blood groups

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- PostgreSQL database
- Virtual environment (recommended)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Initialize database with tables and seed data
python init_db.py
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/donor_near_me
JWT_SECRET_KEY=your-secret-key-here
```

### 5. Run the Application
```bash
python app.py
```

The server will start on `http://localhost:5000`

## Database Schema

### BloodRequest Table
- `blood_request_id` (Primary Key)
- `user_id` (Foreign Key to users)
- `hospital_id` (Foreign Key to hospitals)
- `blood_group_type` (Foreign Key to lookup_blood_groups)
- `no_of_units` (Integer)
- `patient_name` (Text)
- `patient_contact_email` (Text, nullable)
- `patient_contact_phone_number` (Text, nullable)
- `required_by_date` (Date)
- `description` (Text, nullable)
- `status` (Text, default: 'pending')
- `from_date` (Date)
- `to_date` (Date, nullable)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### BloodRequestResponse Table
- `blood_requests_response_id` (Primary Key)
- `blood_request_id` (Foreign Key to blood_requests)
- `user_id` (Foreign Key to users)
- `response_status` (Text)
- `message` (Text, nullable)
- `from_date` (Date)
- `responded_date` (Date, nullable)
- `to_date` (Date, nullable)
- `created_at` (DateTime)
- `updated_at` (DateTime)

## Usage Examples

### 1. Create a Blood Request
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
    "description": "Emergency blood requirement"
  }'
```

### 2. Get All Blood Requests
```bash
curl -X GET http://localhost:5000/blood/requests \
  -H "Authorization: Bearer <your_jwt_token>"
```

### 3. Respond to a Blood Request
```bash
curl -X POST http://localhost:5000/blood/request/123/respond \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "response_status": "accepted",
    "message": "I can donate blood"
  }'
```

## Testing

### Run Test Script
```bash
python test_blood_requests.py
```

This will test all the blood request endpoints and provide detailed output.

### Manual Testing
1. Start the application
2. Use the test script or Postman collection
3. Verify all endpoints work as expected

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

The API provides comprehensive error handling:
- **400 Bad Request**: Validation errors, missing fields
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server errors

## Security Features

- JWT authentication for all protected endpoints
- Password hashing with bcrypt
- Input validation and sanitization
- SQL injection prevention through SQLAlchemy ORM
- CORS configuration for frontend integration

## API Documentation

For detailed API documentation, see `BLOOD_REQUEST_API.md`

## Development Notes

### Adding New Features
1. Update the model if needed
2. Add new routes to `routes/blood_routes.py`
3. Update the test script
4. Update API documentation

### Database Migrations
When making schema changes:
1. Update the model
2. Run database initialization script
3. Test thoroughly

### Testing
- Always test with the provided test script
- Test edge cases and error conditions
- Verify database constraints work correctly

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify database URL in config
   - Ensure database exists

2. **JWT Token Issues**
   - Check JWT_SECRET_KEY is set
   - Verify token format in Authorization header

3. **Import Errors**
   - Ensure all dependencies are installed
   - Check virtual environment is activated

4. **Foreign Key Errors**
   - Run database initialization script
   - Verify lookup data exists

### Debug Mode
Enable debug mode in `app.py` for detailed error messages:
```python
app.run(debug=True)
```

## Contributing

1. Follow the existing code structure
2. Add proper error handling
3. Include tests for new features
4. Update documentation
5. Test thoroughly before submitting

## License

This project is part of the Donor Near Me application. 