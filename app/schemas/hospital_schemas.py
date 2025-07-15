from marshmallow import Schema, fields, validate, ValidationError

class HospitalSchema(Schema):
    """Schema for hospital data"""
    hospital_id = fields.Int(dump_only=True)
    hospital_name = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    hospital_address = fields.Str(validate=validate.Length(max=500))
    hospital_address_lat = fields.Float(validate=validate.Range(min=-90, max=90))
    hospital_address_long = fields.Float(validate=validate.Range(min=-180, max=180))
    hospital_gmap_link = fields.Url()
    has_blood_bank = fields.Bool()
    hospital_contact_number = fields.Str(validate=validate.Length(min=10, max=15))
    hospital_email_id = fields.Email()
    hospital_contact_person = fields.Str(validate=validate.Length(max=100))
    hospital_pincode = fields.Str(validate=validate.Length(min=6, max=10))
    hospital_type = fields.Str(validate=validate.Length(max=50))
    from_date = fields.Date(dump_only=True)
    to_date = fields.Date(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class HospitalRegistrationSchema(Schema):
    """Schema for hospital registration"""
    hospital_name = fields.Str(required=True, validate=validate.Length(min=2, max=200),
                              error_messages={'required': 'Hospital name is required'})
    hospital_address = fields.Str(validate=validate.Length(max=500))
    hospital_address_lat = fields.Float(validate=validate.Range(min=-90, max=90))
    hospital_address_long = fields.Float(validate=validate.Range(min=-180, max=180))
    hospital_gmap_link = fields.Url()
    has_blood_bank = fields.Bool()
    hospital_contact_number = fields.Str(validate=validate.Length(min=10, max=15))
    hospital_email_id = fields.Email()
    hospital_contact_person = fields.Str(validate=validate.Length(max=100))
    hospital_pincode = fields.Str(validate=validate.Length(min=6, max=10))
    hospital_type = fields.Str(validate=validate.Length(max=50)) 