from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from models.user import User

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": "Authentication required"
            }), 401
    return decorated_function

def require_role(required_role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                user = User.query.get(current_user_id)
                
                if not user:
                    return jsonify({
                        "status": "error",
                        "message": "User not found"
                    }), 404
                
                # Check role based on role_id
                if required_role == "super_admin" and user.user_role_id != 1:
                    return jsonify({
                        "status": "error",
                        "message": "Super admin access required"
                    }), 403
                elif required_role == "hospital_admin" and user.user_role_id != 2:
                    return jsonify({
                        "status": "error",
                        "message": "Hospital admin access required"
                    }), 403
                elif required_role == "donor" and user.user_role_id != 3:
                    return jsonify({
                        "status": "error",
                        "message": "Donor access required"
                    }), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": "Authentication required"
                }), 401
        return decorated_function
    return decorator

def get_current_user():
    """Get current authenticated user"""
    try:
        current_user_id = get_jwt_identity()
        return User.query.get(current_user_id)
    except:
        return None

def is_hospital_admin(user):
    """Check if user is hospital admin"""
    return user and user.user_role_id == 2

def is_super_admin(user):
    """Check if user is super admin"""
    return user and user.user_role_id == 1

def is_donor(user):
    """Check if user is donor"""
    return user and user.user_role_id == 3 