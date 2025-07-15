from marshmallow import Schema, fields, validate, ValidationError
import re

class UserSchema(Schema):
    """Schema for user data"""
    user_id = fields.Int(dump_only=True)
    user_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    user_email = fields.Email(required=True)
    user_phone_number = fields.Str(required=True, validate=validate.Length(min=10, max=15))
    blood_group = fields.Str(validate=validate.OneOf(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']))
    address = fields.Str(validate=validate.Length(max=500))
    pincode = fields.Str(validate=validate.Length(min=6, max=10))
    user_role_id = fields.Int(required=True, validate=validate.OneOf([1, 2, 3]))  # 1=super_admin, 2=hospital_admin, 3=donor
    from_date = fields.Date(dump_only=True)
    to_date = fields.Date(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class UserLoginSchema(Schema):
    """Schema for user login"""
    user_email = fields.Email(required=True, error_messages={'required': 'Email is required'})
    password = fields.Str(required=True, validate=validate.Length(min=6), error_messages={'required': 'Password is required'})

class UserRegistrationSchema(Schema):
    """Schema for user registration"""
    user_name = fields.Str(required=True, validate=validate.Length(min=2, max=100), 
                          error_messages={'required': 'Name is required'})
    user_email = fields.Email(required=True, error_messages={'required': 'Email is required'})
    user_phone_number = fields.Str(required=True, validate=validate.Length(min=10, max=15),
                                  error_messages={'required': 'Phone number is required'})
    password = fields.Str(required=True, validate=validate.Length(min=6),
                         error_messages={'required': 'Password is required', 'validator_failed': 'Password must be at least 6 characters'})
    blood_group = fields.Str(validate=validate.OneOf(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']))
    address = fields.Str(validate=validate.Length(max=500))
    pincode = fields.Str(validate=validate.Length(min=6, max=10))
    user_role_id = fields.Int(required=True, validate=validate.OneOf([1, 2, 3]),
                             error_messages={'required': 'Role is required'})

    def validate_phone_number(self, value):
        """Custom validation for phone number"""
        if not re.match(r'^\+?[\d\s\-\(\)]+$', value):
            raise ValidationError('Invalid phone number format')
        return value 