from app import create_app
from db import db
from sqlalchemy import text  # Import text for executing raw SQL

def seed():
    app = create_app()
    with app.app_context():
        # Execute raw SQL for creating tables and seeding data
        with db.engine.connect() as connection:
            # Create Lookup Tables
            connection.execute(text("""
            CREATE TABLE IF NOT EXISTS lookup_blood_groups (
                blood_group_id SERIAL PRIMARY KEY,
                blood_group_name TEXT NOT NULL UNIQUE,
                from_date DATE NOT NULL,
                to_date DATE
            );

            CREATE TABLE IF NOT EXISTS lookup_roles (
                lookup_role_id INT PRIMARY KEY,
                lookup_role_name TEXT NOT NULL UNIQUE CHECK (lookup_role_id IN (0, 1, 2)),
                from_date DATE NOT NULL,
                to_date DATE
            );
            """))

            # Create Hospitals Table
            connection.execute(text("""
            CREATE TABLE IF NOT EXISTS hospitals (
                hospital_id SERIAL PRIMARY KEY,
                hospital_name TEXT NOT NULL,
                hospital_address TEXT,
                hospital_address_lat DOUBLE PRECISION,
                hospital_address_long DOUBLE PRECISION,
                hospital_gmap_link TEXT,
                has_blood_bank BOOLEAN DEFAULT FALSE,
                hospital_contact_number TEXT,
                hospital_email_id TEXT,
                hospital_contact_person TEXT,
                hospital_pincode TEXT,
                hospital_type TEXT,
                from_date DATE NOT NULL,
                to_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """))

            # Create Users Table
            connection.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                user_name TEXT NOT NULL,
                user_email TEXT UNIQUE,
                user_phone_number TEXT UNIQUE,
                blood_group INT REFERENCES lookup_blood_groups(blood_group_id),
                location_lat DOUBLE PRECISION,
                location_lang DOUBLE PRECISION,
                address_line_1 TEXT,
                address_line_2 TEXT,
                pincode TEXT,
                user_role_id INT REFERENCES lookup_roles(lookup_role_id) DEFAULT 2,
                from_date DATE NOT NULL,
                to_date DATE,
                last_donated_date DATE,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """))

            # Create Hospital Admin Linkage Table
            connection.execute(text("""
            CREATE TABLE IF NOT EXISTS user_hospital_admin_lineage (
                user_id INT REFERENCES users(user_id),
                hospital_id INT REFERENCES hospitals(hospital_id),
                from_date DATE NOT NULL,
                to_date DATE,
                PRIMARY KEY (user_id, hospital_id)
            );
            """))

            # Create Hospital Blood Availability Table
            connection.execute(text("""
            CREATE TABLE IF NOT EXISTS hospital_blood_availability (
                hospital_id INT REFERENCES hospitals(hospital_id),
                blood_group_id INT REFERENCES lookup_blood_groups(blood_group_id),
                no_of_units INT NOT NULL,
                from_date DATE NOT NULL,
                to_date DATE,
                PRIMARY KEY (hospital_id, blood_group_id)
            );
            """))

            # Create Blood Requests Table
            connection.execute(text("""
            CREATE TABLE IF NOT EXISTS blood_requests (
                blood_request_id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(user_id),
                hospital_id INT REFERENCES hospitals(hospital_id),
                blood_group_type INT REFERENCES lookup_blood_groups(blood_group_id),
                no_of_units INT NOT NULL,
                patient_name TEXT NOT NULL,
                patient_contact_email TEXT,
                patient_contact_phone_number TEXT,
                required_by_date DATE NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'fulfilled', 'expired', 'cancelled')),
                from_date DATE NOT NULL,
                to_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """))

            # Create Blood Request Responses Table
            connection.execute(text("""
            CREATE TABLE IF NOT EXISTS blood_requests_responses (
                blood_requests_response_id SERIAL PRIMARY KEY,
                blood_request_id INT REFERENCES blood_requests(blood_request_id),
                user_id INT REFERENCES users(user_id),
                response_status TEXT CHECK (response_status IN ('accepted', 'declined', 'pending')),
                message TEXT,
                from_date DATE NOT NULL,
                responded_date DATE,
                to_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """))

            # Create Device Tokens Table
            connection.execute(text("""
            CREATE TABLE IF NOT EXISTS user_device_tokens (
                user_id INT REFERENCES users(user_id),
                firebase_device_token TEXT NOT NULL,
                platform TEXT CHECK (platform IN ('ios', 'android', 'web')),
                last_seen_date TIMESTAMP,
                PRIMARY KEY (user_id, firebase_device_token)
            );
            """))

            # Seed Lookup Tables
            connection.execute(text("""
            INSERT INTO lookup_roles (lookup_role_id, lookup_role_name, from_date)
            VALUES (0, 'super_admin', CURRENT_DATE),
                   (1, 'hospital_admin', CURRENT_DATE),
                   (2, 'user', CURRENT_DATE),
                   (3, 'donor', CURRENT_DATE)  -- Added donor role
            ON CONFLICT DO NOTHING;

            INSERT INTO lookup_blood_groups (blood_group_name, from_date)
            VALUES ('A+', CURRENT_DATE),
                   ('A-', CURRENT_DATE),
                   ('B+', CURRENT_DATE),
                   ('B-', CURRENT_DATE),
                   ('AB+', CURRENT_DATE),
                   ('AB-', CURRENT_DATE),
                   ('O+', CURRENT_DATE),
                   ('O-', CURRENT_DATE)
            ON CONFLICT DO NOTHING;
            """))

            # Seed Users
            connection.execute(text("""
            INSERT INTO users (user_name, password, user_email, user_phone_number, user_role_id, from_date, created_at, updated_at)
            VALUES
                ('a', 'a', 'a@a.com', '1111111111', 0, CURRENT_DATE, NOW(), NOW()), -- super admin
                ('b', 'b', 'b@b.com', '2222222222', 3, CURRENT_DATE, NOW(), NOW()), -- donor
                ('c', 'c', 'c@c.com', '3333333333', 1, CURRENT_DATE, NOW(), NOW())  -- hospital admin
            ON CONFLICT (user_email) DO NOTHING;
            """))

            print("Tables created, lookup data and users seeded successfully.")

if __name__ == '__main__':
    seed()
