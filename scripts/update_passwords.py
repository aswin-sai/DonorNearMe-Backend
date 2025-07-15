import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from db import db
from models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    users = User.query.all()
    for user in users:
        if user.password == 'default_password':  # Check for the default password
            user.password = generate_password_hash('password123')  # Replace with a hashed password
            print(f"👀 Updated password for user: {user.user_name}")
    db.session.commit()
    print("👀 Passwords updated successfully.")
