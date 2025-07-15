from marshmallow import Schema, fields

class DonationSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    blood_request_id = fields.Int()
    scheduled_date = fields.DateTime(required=True)
    status = fields.Str()
    certificate = fields.Str()
    created_at = fields.DateTime() 