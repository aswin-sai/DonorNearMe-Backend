from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, LookupRole
from datetime import datetime, timedelta
import logging

auth_bp = Blueprint('auth', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Role mapping dictionary
ROLE_MAPPING = {
    "super_admin": 1,
    "hospital_admin": 2,
    "donor": 3
}

def map_role_to_id(role_name):
    """
    Maps a role string to its corresponding role ID.

    Args:
        role_name (str): The role name as a string.

    Returns:
        int: The corresponding role ID if valid.
        None: If the role is invalid.
    """
    return ROLE_MAPPING.get(role_name.lower())

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    logging.debug(f"Incoming registration data: {data}")

    # Map frontend field names to backend field names
    user_name = data.get('user_name') or data.get('fullname')
    blood_group = data.get('bloodgroup') or data.get('blood_group')
    address = data.get('address')
    pincode = int(data.get('pincode')) if data.get('pincode') else None
    password = data.get('password')
    role_name = data.get('role', 'donor')  # Default role is donor
    user_email = data.get('user_email') or data.get('emailaddress')
    user_phone_number = str(data.get('user_phone_number') or data.get('phonenumber'))

    # Validate required fields
    missing_fields = []
    if not user_name:
        missing_fields.append('fullname')
    if not password:
        missing_fields.append('password')
    if not user_email:
        missing_fields.append('emailaddress')
    if not user_phone_number:
        missing_fields.append('phonenumber')
    if not blood_group:
        missing_fields.append('bloodgroup')
    if not address:
        missing_fields.append('address')
    if not pincode:
        missing_fields.append('pincode')

    if missing_fields:
        logging.error(f"Missing required fields: {missing_fields}")
        return jsonify({'message': f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Map role name to role ID
    role_id = map_role_to_id(role_name)
    if role_id is None:
        logging.error(f"Invalid role: {role_name}")
        return jsonify({'message': 'Invalid role'}), 400

    # Check if email or phone number already exists
    if User.query.filter_by(user_email=user_email).first():
        logging.error(f"Email already exists: {user_email}")
        return jsonify({'message': 'Email already exists'}), 409
    if User.query.filter_by(user_phone_number=user_phone_number).first():
        logging.error(f"Phone number already exists: {user_phone_number}")
        return jsonify({'message': 'Phone number already exists'}), 409

    # Create new user
    new_user = User(
        user_name=user_name,
        blood_group=blood_group,
        address=address,
        pincode=pincode,
        password=password,
        user_email=user_email,
        user_phone_number=user_phone_number,
        user_role_id=role_id,
        from_date=datetime.utcnow().date()
    )

    db.session.add(new_user)
    db.session.commit()

    logging.info(f"User registered successfully: {user_name}")
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    logging.debug(f"Incoming login data: {data}")

    if not data:
        logging.error("Invalid or missing JSON body")
        return jsonify({'success': False, 'message': 'Invalid or missing JSON body'}), 400

    # Use 'user_email' if present, fallback to 'emailaddress'
    user_email = data.get('user_email') or data.get('emailaddress')
    password = data.get('password')

    if not user_email or not password:
        logging.error("Missing required fields: user_email and password required")
        return jsonify({'success': False, 'message': 'Missing required fields: user_email and password required'}), 400

    user = User.query.filter_by(user_email=user_email).first()

    if not user:
        logging.error(f"User not found for email: {user_email}")
        return jsonify({'success': False, 'message': 'User not found'}), 404

    if not user.check_password(password):
        logging.error("Invalid password")
        return jsonify({'success': False, 'message': 'Invalid password'}), 401

    # Create token with user_id as identity (not a dict)
    access_token = create_access_token(
        identity=str(user.user_id),
        expires_delta=timedelta(hours=1)
    )

    logging.info(f"User logged in successfully: {user_email}")
    return jsonify({
        'success': True, 
        'message': 'Login successful', 
        'access_token': access_token,
        'token': access_token  # Keep both for compatibility
    }), 200

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user:
        return jsonify({
            'message': f'Hello, user {user.user_name}!',
            'user_id': user.user_id,
            'user_role_id': user.user_role_id
        }), 200
    else:
        return jsonify({'message': 'User not found'}), 404

@auth_bp.route('/hospital-admin-login', methods=['POST'])
def hospital_admin_login():
    data = request.get_json(silent=True)
    logging.debug(f"Incoming hospital admin login data: {data}")

    if not data:
        logging.error("Invalid or missing JSON body")
        return jsonify({'success': False, 'message': 'Invalid or missing JSON body'}), 400

    # Accept 'email' or 'user_email' for flexibility
    user_email = data.get('email') or data.get('user_email')
    password = data.get('password')

    if not user_email or not password:
        logging.error("Missing required fields: email and password required")
        return jsonify({'success': False, 'message': 'Missing required fields: email and password required'}), 400

    # Get the role_id for hospital_admin
    hospital_admin_role_id = map_role_to_id('hospital_admin')
    user = User.query.filter_by(user_email=user_email, user_role_id=hospital_admin_role_id).first()

    if not user:
        logging.error(f"Hospital admin not found or not authorized for email: {user_email}")
        return jsonify({'success': False, 'message': 'Unauthorized: Only hospital admins can login here'}), 401

    if not user.check_password(password):
        logging.error("Invalid password for hospital admin login")
        return jsonify({'success': False, 'message': 'Invalid password'}), 401

    access_token = create_access_token(
        identity=str(user.user_id),
        expires_delta=timedelta(hours=1)
    )

    logging.info(f"Hospital admin logged in successfully: {user_email}")
    return jsonify({
        'success': True,
        'message': 'Hospital admin login successful',
        'access_token': access_token,
        'token': access_token
    }), 200