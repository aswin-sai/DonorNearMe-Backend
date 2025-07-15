from marshmallow import Schema, fields

class BloodRequestSchema(Schema):
    id = fields.Int(dump_only=True)
    patient_name = fields.Str(required=True)
    patient_contact = fields.Str(required=True)
    blood_group_id = fields.Int(required=True)
    hospital_id = fields.Int(required=True)
    status = fields.Str()
    created_by = fields.Int()
    created_at = fields.DateTime()
    updated_at = fields.DateTime() 