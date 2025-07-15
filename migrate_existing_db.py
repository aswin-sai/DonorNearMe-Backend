from app import create_app, db
from sqlalchemy import text

def migrate_existing_database():
    """Add missing columns to existing tables"""
    app = create_app()
    
    with app.app_context():
        try:
            # Add created_at and updated_at columns to existing tables
            tables_to_migrate = [
                'lookup_roles',
                'lookup_blood_groups',
                'users',
                'hospitals',
                'blood_requests',
                'blood_requests_responses',
                'hospital_blood_availability',
                'user_hospital_admin_lineage',
                'user_device_tokens'
            ]
            
            for table in tables_to_migrate:
                try:
                    # Check if created_at column exists
                    result = db.session.execute(text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = '{table}' AND column_name = 'created_at'
                    """))
                    
                    if not result.fetchone():
                        print(f"Adding created_at column to {table}")
                        db.session.execute(text(f"""
                            ALTER TABLE {table} 
                            ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        """))
                    
                    # Check if updated_at column exists
                    result = db.session.execute(text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = '{table}' AND column_name = 'updated_at'
                    """))
                    
                    if not result.fetchone():
                        print(f"Adding updated_at column to {table}")
                        db.session.execute(text(f"""
                            ALTER TABLE {table} 
                            ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        """))
                        
                except Exception as e:
                    print(f"Error migrating table {table}: {e}")
                    continue
            
            db.session.commit()
            print("Database migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {e}")
            raise

if __name__ == '__main__':
    migrate_existing_database() 