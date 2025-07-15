from marshmallow import Schema, fields

class HospitalSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    address = fields.Str(required=True)
    phone = fields.Str(required=True)
    email = fields.Str(required=True)
    inventory = fields.Dict()
    created_at = fields.DateTime() 