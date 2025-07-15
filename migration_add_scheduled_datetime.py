from app import create_app, db
from sqlalchemy import text

app = create_app()
app.app_context().push()

# Add the scheduled_datetime column
with db.engine.connect() as conn:
    conn.execute(text("""
        ALTER TABLE blood_requests_responses 
        ADD COLUMN scheduled_datetime TIMESTAMP NULL;
    """))
    conn.commit()

print("✓ Added scheduled_datetime column to blood_requests_responses table") 