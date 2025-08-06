# Donor Near Me - Backend API

A production-ready Flask API for managing blood donation requests and hospital coordination.

## 🚀 Features

- **User Authentication**: JWT-based authentication with role-based access control
- **Hospital Management**: Register and manage hospitals with blood bank information
- **Blood Request System**: Create, manage, and respond to blood donation requests
- **Database Migrations**: Flask-Migrate for database schema management
- **Input Validation**: Marshmallow schemas for request validation
- **Error Handling**: Comprehensive error handling with structured responses
- **Security**: Password hashing, CORS protection, and JWT token management

## 📁 Project Structure

```
backend/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── routes/          # Flask blueprints
│   ├── schemas/         # Marshmallow validation schemas
│   ├── controllers/     # Business logic (if needed)
│   ├── utils/           # Helper functions
│   └── __init__.py      # Application factory
├── config.py            # Configuration classes
├── run.py              # Application entry point
├── migrations.py       # Database initialization
├── requirements.txt    # Python dependencies
└── env.example         # Environment variables template
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python migrations.py
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

## 🔧 Configuration

### Environment Variables

- `FLASK_ENV`: Application environment (development/production)
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `CORS_ORIGINS`: Allowed CORS origins

### Database Setup

1. Create PostgreSQL database
2. Update `DATABASE_URL` in `.env`
3. Run `python migrations.py` to initialize tables

## 📚 API Documentation

### Authentication Endpoints

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### Hospital Endpoints

- `GET /hospital` - List all hospitals
- `POST /hospital` - Register new hospital
- `GET /hospital/<id>` - Get hospital details
- `PUT /hospital/<id>` - Update hospital

### Blood Request Endpoints

- `GET /blood/request` - List blood requests
- `POST /blood/request` - Create blood request
- `GET /blood/request/<id>` - Get request details
- `POST /blood/request/<id>/respond` - Respond to request

## 🔐 Security Features

- **Password Hashing**: Using Werkzeug's security functions
- **JWT Tokens**: Secure token-based authentication
- **Role-Based Access**: Different permissions for different user roles
- **Input Validation**: Comprehensive request validation
- **CORS Protection**: Configurable cross-origin resource sharing

## 🗄️ Database Models

### Core Models

- **User**: User accounts with role-based access
- **Hospital**: Hospital information and blood bank details
- **BloodRequest**: Blood donation requests
- **BloodRequestResponse**: Responses to blood requests
- **LookupRole**: User roles (Super Admin, Hospital Admin, Donor)
- **LookupBloodGroup**: Blood group types

### Relationships

- Users can be associated with hospitals (admin lineage)
- Blood requests are linked to users and hospitals
- Responses are linked to requests and users

## 🚀 Production Deployment

1. **Set production environment**
   ```bash
   export FLASK_ENV=production
   ```

2. **Use Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

3. **Set up reverse proxy** (Nginx recommended)

4. **Configure SSL certificates**

## 🧪 Testing

Run tests with:
```bash
python -m pytest tests/
```

## 📝 API Response Format

All API responses follow this structure:

### Success Response
```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "data": { ... }
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Error description",
  "errors": { ... }  // Optional validation errors
}
```

## 🔄 Database Migrations

The application uses Flask-Migrate for database migrations:

```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.


DDL for the DonorNearMe
-- Table: public.blood_requests

-- DROP TABLE IF EXISTS public.blood_requests;

CREATE TABLE IF NOT EXISTS public.blood_requests
(
    blood_request_id integer NOT NULL DEFAULT nextval('blood_requests_blood_request_id_seq'::regclass),
    user_id integer NOT NULL,
    hospital_id integer NOT NULL,
    blood_group_type integer NOT NULL,
    no_of_units integer NOT NULL,
    patient_name character varying(120) COLLATE pg_catalog."default" NOT NULL,
    patient_contact_email character varying(120) COLLATE pg_catalog."default",
    patient_contact_phone_number character varying(20) COLLATE pg_catalog."default",
    required_by_date date,
    description text COLLATE pg_catalog."default",
    status character varying(20) COLLATE pg_catalog."default" DEFAULT 'pending'::character varying,
    from_date date,
    to_date date,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    CONSTRAINT blood_requests_pkey PRIMARY KEY (blood_request_id),
    CONSTRAINT blood_requests_blood_group_type_fkey FOREIGN KEY (blood_group_type)
        REFERENCES public.lookup_blood_groups (blood_group_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT blood_requests_hospital_id_fkey FOREIGN KEY (hospital_id)
        REFERENCES public.hospitals (hospital_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT blood_requests_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.blood_requests
    OWNER to postgres;



-- Table: public.blood_requests_responses

-- DROP TABLE IF EXISTS public.blood_requests_responses;

CREATE TABLE IF NOT EXISTS public.blood_requests_responses
(
    blood_requests_response_id integer NOT NULL DEFAULT nextval('blood_requests_responses_blood_requests_response_id_seq'::regclass),
    blood_request_id integer NOT NULL,
    user_id integer NOT NULL,
    response_status text COLLATE pg_catalog."default" NOT NULL,
    message text COLLATE pg_catalog."default",
    from_date date NOT NULL,
    responded_date date,
    to_date date,
    scheduled_datetime timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    CONSTRAINT blood_requests_responses_pkey PRIMARY KEY (blood_requests_response_id),
    CONSTRAINT blood_requests_responses_blood_request_id_fkey FOREIGN KEY (blood_request_id)
        REFERENCES public.blood_requests (blood_request_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT blood_requests_responses_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.blood_requests_responses
    OWNER to postgres;




-- Table: public.donations

-- DROP TABLE IF EXISTS public.donations;

CREATE TABLE IF NOT EXISTS public.donations
(
    id integer NOT NULL DEFAULT nextval('donations_id_seq'::regclass),
    user_id integer NOT NULL,
    blood_request_id integer,
    scheduled_date timestamp without time zone NOT NULL,
    status character varying(20) COLLATE pg_catalog."default" DEFAULT 'scheduled'::character varying,
    certificate character varying(255) COLLATE pg_catalog."default",
    created_at timestamp without time zone,
    CONSTRAINT donations_pkey PRIMARY KEY (id),
    CONSTRAINT donations_blood_request_id_fkey FOREIGN KEY (blood_request_id)
        REFERENCES public.blood_requests (blood_request_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT donations_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.donations
    OWNER to postgres;




-- Table: public.hospital_blood_availability

-- DROP TABLE IF EXISTS public.hospital_blood_availability;

CREATE TABLE IF NOT EXISTS public.hospital_blood_availability
(
    hospital_id integer NOT NULL,
    blood_group_id integer NOT NULL,
    no_of_units integer NOT NULL,
    from_date date NOT NULL,
    to_date date,
    CONSTRAINT hospital_blood_availability_pkey PRIMARY KEY (hospital_id, blood_group_id),
    CONSTRAINT hospital_blood_availability_blood_group_id_fkey FOREIGN KEY (blood_group_id)
        REFERENCES public.lookup_blood_groups (blood_group_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT hospital_blood_availability_hospital_id_fkey FOREIGN KEY (hospital_id)
        REFERENCES public.hospitals (hospital_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.hospital_blood_availability
    OWNER to postgres;



-- Table: public.hospitals

-- DROP TABLE IF EXISTS public.hospitals;

CREATE TABLE IF NOT EXISTS public.hospitals
(
    hospital_id integer NOT NULL DEFAULT nextval('hospitals_hospital_id_seq'::regclass),
    hospital_name character varying(120) COLLATE pg_catalog."default" NOT NULL,
    hospital_address character varying(255) COLLATE pg_catalog."default",
    hospital_address_lat double precision,
    hospital_address_long double precision,
    hospital_gmap_link character varying(500) COLLATE pg_catalog."default",
    has_blood_bank boolean DEFAULT false,
    hospital_contact_number character varying(20) COLLATE pg_catalog."default",
    hospital_email_id character varying(120) COLLATE pg_catalog."default",
    hospital_contact_person character varying(120) COLLATE pg_catalog."default",
    hospital_pincode character varying(10) COLLATE pg_catalog."default",
    hospital_type character varying(50) COLLATE pg_catalog."default",
    from_date date NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    to_date date,
    CONSTRAINT hospitals_pkey PRIMARY KEY (hospital_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.hospitals
    OWNER to postgres;



-- Table: public.lookup_blood_groups

-- DROP TABLE IF EXISTS public.lookup_blood_groups;

CREATE TABLE IF NOT EXISTS public.lookup_blood_groups
(
    blood_group_id integer NOT NULL DEFAULT nextval('lookup_blood_groups_blood_group_id_seq'::regclass),
    blood_group_name text COLLATE pg_catalog."default" NOT NULL,
    from_date date NOT NULL,
    to_date date,
    CONSTRAINT lookup_blood_groups_pkey PRIMARY KEY (blood_group_id),
    CONSTRAINT lookup_blood_groups_blood_group_name_key UNIQUE (blood_group_name)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.lookup_blood_groups
    OWNER to postgres;



-- Table: public.lookup_roles

-- DROP TABLE IF EXISTS public.lookup_roles;

CREATE TABLE IF NOT EXISTS public.lookup_roles
(
    lookup_role_id integer NOT NULL DEFAULT nextval('lookup_roles_lookup_role_id_seq'::regclass),
    lookup_role_name text COLLATE pg_catalog."default" NOT NULL,
    from_date date NOT NULL,
    to_date date,
    CONSTRAINT lookup_roles_pkey PRIMARY KEY (lookup_role_id),
    CONSTRAINT lookup_roles_lookup_role_name_key UNIQUE (lookup_role_name)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.lookup_roles
    OWNER to postgres;



-- Table: public.notifications

-- DROP TABLE IF EXISTS public.notifications;

CREATE TABLE IF NOT EXISTS public.notifications
(
    id integer NOT NULL DEFAULT nextval('notifications_id_seq'::regclass),
    user_id integer NOT NULL,
    message character varying(255) COLLATE pg_catalog."default" NOT NULL,
    is_read boolean DEFAULT false,
    action_url character varying(255) COLLATE pg_catalog."default",
    created_at timestamp without time zone,
    CONSTRAINT notifications_pkey PRIMARY KEY (id),
    CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.notifications
    OWNER to postgres;



-- Table: public.user_device_tokens

-- DROP TABLE IF EXISTS public.user_device_tokens;

CREATE TABLE IF NOT EXISTS public.user_device_tokens
(
    user_id integer NOT NULL,
    firebase_device_token text COLLATE pg_catalog."default" NOT NULL,
    platform text COLLATE pg_catalog."default" NOT NULL,
    last_seen_date timestamp without time zone,
    CONSTRAINT user_device_tokens_pkey PRIMARY KEY (user_id, firebase_device_token),
    CONSTRAINT user_device_tokens_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.user_device_tokens
    OWNER to postgres;


-- Table: public.user_hospital_admin_lineage

-- DROP TABLE IF EXISTS public.user_hospital_admin_lineage;

CREATE TABLE IF NOT EXISTS public.user_hospital_admin_lineage
(
    user_id integer NOT NULL,
    hospital_id integer NOT NULL,
    from_date date NOT NULL,
    to_date date,
    CONSTRAINT user_hospital_admin_lineage_pkey PRIMARY KEY (user_id, hospital_id),
    CONSTRAINT user_hospital_admin_lineage_hospital_id_fkey FOREIGN KEY (hospital_id)
        REFERENCES public.hospitals (hospital_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT user_hospital_admin_lineage_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.user_hospital_admin_lineage
    OWNER to postgres;


-- Table: public.users

-- DROP TABLE IF EXISTS public.users;

CREATE TABLE IF NOT EXISTS public.users
(
    user_id integer NOT NULL DEFAULT nextval('users_user_id_seq'::regclass),
    user_name text COLLATE pg_catalog."default" NOT NULL,
    blood_group character varying(5) COLLATE pg_catalog."default",
    address text COLLATE pg_catalog."default",
    pincode character varying(10) COLLATE pg_catalog."default",
    user_email text COLLATE pg_catalog."default" NOT NULL,
    user_phone_number character varying(15) COLLATE pg_catalog."default" NOT NULL,
    password character varying(256) COLLATE pg_catalog."default" NOT NULL,
    user_role_id integer NOT NULL,
    from_date date NOT NULL,
    to_date date,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    CONSTRAINT users_pkey PRIMARY KEY (user_id),
    CONSTRAINT users_user_email_key UNIQUE (user_email),
    CONSTRAINT users_user_phone_number_key UNIQUE (user_phone_number),
    CONSTRAINT users_user_role_id_fkey FOREIGN KEY (user_role_id)
        REFERENCES public.lookup_roles (lookup_role_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.users
    OWNER to postgres;



