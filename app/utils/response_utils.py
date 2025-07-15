from flask import jsonify
from functools import wraps

def success_response(data=None, message="Success", status_code=200):
    """Create a success response"""
    response = {
        "status": "success",
        "message": message,
        "data": data
    }
    return jsonify(response), status_code

def error_response(message="An error occurred", status_code=400, errors=None):
    """Create an error response"""
    response = {
        "status": "error",
        "message": message
    }
    if errors:
        response["errors"] = errors
    return jsonify(response), status_code

def validation_error_response(errors, message="Validation failed"):
    """Create a validation error response"""
    return error_response(message=message, status_code=422, errors=errors)

def handle_exceptions(f):
    """Decorator to handle exceptions in routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return error_response(str(e), 500)
    return decorated_function 