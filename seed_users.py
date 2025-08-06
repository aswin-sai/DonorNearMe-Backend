from app import create_app
from db import db
from sqlalchemy import text

def seed_users():
    app = create_app()
    with app.app_context():
        with db.engine.begin() as connection:
            # Ensure lookup_roles exist
            connection.execute(text("""
            INSERT INTO lookup_roles (lookup_role_id, lookup_role_name, from_date)
            VALUES
                (0, 'super_admin', CURRENT_DATE),
                (1, 'hospital_admin', CURRENT_DATE),
                (2, 'user', CURRENT_DATE),
                (3, 'donor', CURRENT_DATE)
            ON CONFLICT (lookup_role_id) DO NOTHING;
            """))
            # Ensure lookup_blood_groups exist
            connection.execute(text("""
            INSERT INTO lookup_blood_groups (blood_group_name, from_date)
            VALUES
                ('A+', CURRENT_DATE),
                ('A-', CURRENT_DATE),
                ('B+', CURRENT_DATE),
                ('B-', CURRENT_DATE),
                ('AB+', CURRENT_DATE),
                ('AB-', CURRENT_DATE),
                ('O+', CURRENT_DATE),
                ('O-', CURRENT_DATE)
            ON CONFLICT (blood_group_name) DO NOTHING;
            """))
            # Insert a demo hospital with all main fields (allow duplicates)
            connection.execute(text("""
            INSERT INTO hospitals (
                hospital_name, hospital_address, hospital_address_lat, hospital_address_long, hospital_gmap_link, has_blood_bank, hospital_contact_number, hospital_email_id, hospital_contact_person, hospital_pincode, hospital_type, from_date, created_at, updated_at
            ) VALUES (
                'Demo Hospital', '123 Main St', 12.9716, 77.5946, 'https://maps.google.com/?q=12.9716,77.5946', TRUE, '1234567890', 'demo@hospital.com', 'Dr. Demo', '560001', 'General', CURRENT_DATE, NOW(), NOW()
            );
            """))
            # Seed Users (add more donors)
            connection.execute(text("""
            INSERT INTO users (user_name, password, user_email, user_phone_number, user_role_id, from_date, created_at, updated_at)
            VALUES
                ('a', 'a', 'a@a.com', '1111111111', 0, CURRENT_DATE, NOW(), NOW()), -- super admin
                ('b', 'b', 'b@b.com', '2222222222', 3, CURRENT_DATE, NOW(), NOW()), -- donor
                ('c', 'c', 'c@c.com', '3333333333', 1, CURRENT_DATE, NOW(), NOW()), -- hospital admin
                ('donor2', 'd2', 'd2@d.com', '4444444444', 3, CURRENT_DATE, NOW(), NOW()), -- donor
                ('donor3', 'd3', 'd3@d.com', '5555555555', 3, CURRENT_DATE, NOW(), NOW())  -- donor
            ON CONFLICT (user_email) DO NOTHING;
            """))
            # Get a single hospital_id for Demo Hospital
            hospital_id_result = connection.execute(text("""
                SELECT MIN(hospital_id) as hospital_id FROM hospitals WHERE hospital_name = 'Demo Hospital'
            """)).fetchone()
            hospital_id = hospital_id_result[0] if hospital_id_result else None
            # Link admin user to demo hospital
            admin_user_id = connection.execute(text("SELECT user_id FROM users WHERE user_email = 'c@c.com' ")).scalar()
            if admin_user_id and hospital_id:
                connection.execute(text(f'''
                    INSERT INTO user_hospital_admin_lineage (user_id, hospital_id, from_date)
                    VALUES ({admin_user_id}, {hospital_id}, CURRENT_DATE)
                    ON CONFLICT DO NOTHING;
                '''))
                # Seed blood inventory for demo hospital (all blood groups, 10 units each)
                connection.execute(text(f"""
                INSERT INTO hospital_blood_availability (hospital_id, blood_group_id, no_of_units, from_date)
                SELECT {hospital_id}, bg.blood_group_id, 10, CURRENT_DATE
                FROM lookup_blood_groups bg
                ON CONFLICT (hospital_id, blood_group_id) DO NOTHING;
                """))
                # Seed a blood request for demo hospital
                connection.execute(text(f"""
                INSERT INTO blood_requests (
                    user_id, hospital_id, blood_group_type, no_of_units, patient_name, required_by_date, status, from_date, created_at, updated_at
                )
                SELECT u.user_id, {hospital_id}, bg.blood_group_id, 2, 'John Doe', CURRENT_DATE + INTERVAL '2 days', 'pending', CURRENT_DATE, NOW(), NOW()
                FROM users u, lookup_blood_groups bg
                WHERE u.user_email = 'b@b.com' AND bg.blood_group_name = 'A+'
                ON CONFLICT DO NOTHING;
                """))
            print("Roles, blood groups, hospital, users, admin-hospital link, blood inventory, and a blood request seeded successfully.")

if __name__ == '__main__':
    seed_users() 