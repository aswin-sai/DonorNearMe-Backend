from app import create_app
from db import db
from models.hospital import Hospital

app = create_app()
with app.app_context():
    num_deleted = Hospital.query.delete()
    db.session.commit()
    print(f"Deleted {num_deleted} hospitals.")