from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE
from datetime import datetime, date

class BloodRequestSchema(Schema):
    """Schema for blood request validation"""
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields
    
    hospital_id = fields.Raw(required=True)  # Accept any type, we'll convert to int
    blood_group_type = fields.Raw(required=True)  # Accept any type, we'll handle conversion in the route
    no_of_units = fields.Integer(required=True, validate=validate.Range(min=1, max=100))
    patient_name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    patient_contact_email = fields.Email(allow_none=True)
    patient_contact_phone_number = fields.Str(allow_none=True, validate=validate.Length(max=20))
    required_by_date = fields.Date(required=True)
    description = fields.Str(allow_none=True, validate=validate.Length(max=1000))
    status = fields.Str(validate=validate.OneOf(['pending', 'accepted', 'cancelled', 'completed', 'Pending', 'Accepted', 'Cancelled', 'Completed']), missing='pending')

    def validate_required_by_date(self, value):
        """Validate that required_by_date is not in the past"""
        if value < date.today():
            raise ValidationError('Required by date cannot be in the past')

class BloodRequestResponseSchema(Schema):
    """Schema for blood request response validation"""
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields like from_date, to_date
    
    response_status = fields.Str(required=True, validate=validate.OneOf(['accepted', 'declined']))
    message = fields.Str(allow_none=True, validate=validate.Length(max=500))
    scheduled_datetime = fields.DateTime(allow_none=True)

class HospitalSchema(Schema):
    """Schema for hospital validation"""
    hospital_name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    hospital_address = fields.Str(allow_none=True, validate=validate.Length(max=500))
    hospital_contact_number = fields.Str(allow_none=True, validate=validate.Length(max=20))
    hospital_email_id = fields.Email(allow_none=True)
    hospital_contact_person = fields.Str(allow_none=True, validate=validate.Length(max=255))
    hospital_pincode = fields.Str(allow_none=True, validate=validate.Length(max=10))
    hospital_type = fields.Str(allow_none=True, validate=validate.Length(max=100))
    has_blood_bank = fields.Boolean(missing=False) 