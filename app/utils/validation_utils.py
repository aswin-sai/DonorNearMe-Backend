from flask import request
from marshmallow import ValidationError
from app.utils.response_utils import validation_error_response

def validate_request_data(schema_class, data):
    """Validate request data using marshmallow schema"""
    try:
        schema = schema_class()
        validated_data = schema.load(data)
        return validated_data, None
    except ValidationError as e:
        return None, validation_error_response(e.messages)

def validate_json_request(f):
    """Decorator to validate JSON request"""
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return validation_error_response({"json": ["Request must be JSON"]})
        return f(*args, **kwargs)
    return decorated_function 