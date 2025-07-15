from db import db

class LookupRole(db.Model):
    __tablename__ = 'lookup_roles'

    lookup_role_id = db.Column(db.Integer, primary_key=True)
    lookup_role_name = db.Column(db.Text, nullable=False, unique=True)
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=True)


class LookupBloodGroup(db.Model):
    __tablename__ = 'lookup_blood_groups'

    blood_group_id = db.Column(db.Integer, primary_key=True)
    blood_group_name = db.Column(db.Text, nullable=False, unique=True)
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=True)