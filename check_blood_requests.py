from app import create_app
from models.blood_request import BloodRequest
from models.user import User

app = create_app()
app.app_context().push()

# Get all blood requests
requests = BloodRequest.query.all()
print(f'Total blood requests: {len(requests)}')

for req in requests:
    print(f'ID: {req.blood_request_id}, User ID: {req.user_id}, Status: {req.status}')

# Get user details for each request
print("\nDetailed blood requests:")
for req in requests:
    user = User.query.get(req.user_id)
    user_name = user.user_name if user else "Unknown"
    print(f'ID: {req.blood_request_id}, User: {user_name} (ID: {req.user_id}), Status: {req.status}') 