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