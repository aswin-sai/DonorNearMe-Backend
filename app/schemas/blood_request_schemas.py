from marshmallow import Schema, fields, validate, ValidationError
from datetime import date, datetime

class BloodRequestSchema(Schema):
    """Schema for blood request data"""
    blood_request_id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    hospital_id = fields.Int(required=True)
    blood_group_type = fields.Int(required=True)
    no_of_units = fields.Int(required=True, validate=validate.Range(min=1, max=100))
    patient_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    patient_contact_email = fields.Email()
    patient_contact_phone_number = fields.Str(validate=validate.Length(min=10, max=15))
    required_by_date = fields.Date(required=True)
    description = fields.Str(validate=validate.Length(max=1000))
    status = fields.Str(validate=validate.OneOf(['pending', 'active', 'completed', 'cancelled']))
    from_date = fields.Date(dump_only=True)
    to_date = fields.Date(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class BloodRequestResponseSchema(Schema):
    """Schema for blood request response"""
    blood_requests_response_id = fields.Int(dump_only=True)
    blood_request_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    response_status = fields.Str(required=True, validate=validate.OneOf(['accepted', 'declined', 'pending']))
    message = fields.Str(validate=validate.Length(max=500))
    from_date = fields.Date(dump_only=True)
    responded_date = fields.Date(dump_only=True)
    to_date = fields.Date(dump_only=True)
    scheduled_datetime = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class CreateBloodRequestSchema(Schema):
    """Schema for creating blood request"""
    hospital_id = fields.Int(required=True, error_messages={'required': 'Hospital ID is required'})
    blood_group_type = fields.Int(required=True, error_messages={'required': 'Blood group is required'})
    no_of_units = fields.Int(required=True, validate=validate.Range(min=1, max=100),
                            error_messages={'required': 'Number of units is required'})
    patient_name = fields.Str(required=True, validate=validate.Length(min=2, max=100),
                             error_messages={'required': 'Patient name is required'})
    patient_contact_email = fields.Email()
    patient_contact_phone_number = fields.Str(validate=validate.Length(min=10, max=15))
    required_by_date = fields.Date(required=True, error_messages={'required': 'Required by date is required'})
    description = fields.Str(validate=validate.Length(max=1000))

    def validate_required_by_date(self, value):
        """Custom validation for required by date"""
        if value and value < date.today():
            raise ValidationError('Required by date cannot be in the past')
        return value

class RespondToBloodRequestSchema(Schema):
    """Schema for responding to blood request"""
    response_status = fields.Str(required=True, validate=validate.OneOf(['accepted', 'declined']),
                                error_messages={'required': 'Response status is required'})
    message = fields.Str(validate=validate.Length(max=500))
    scheduled_datetime = fields.DateTime()

    def validate_scheduled_datetime(self, value):
        """Custom validation for scheduled datetime"""
        if value and value < datetime.utcnow():
            raise ValidationError('Scheduled datetime cannot be in the past')
        return value 