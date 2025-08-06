import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # 🔧 JWT Configuration fixes for token verification
    JWT_ALGORITHM = 'HS256'
    JWT_DECODE_AUDIENCE = None  # Allow any audience
    JWT_VERIFY_SUB = False  # Don't strictly verify subject format
    JWT_IDENTITY_CLAIM = 'sub'  # Standard claim name
    JWT_ERROR_MESSAGE_KEY = 'message'  # Consistent error message key
    
    # Additional JWT settings to prevent verification failures
    JWT_VERIFY_CLAIMS = ['signature', 'exp', 'iat']  # Only verify essential claims
    JWT_REQUIRED_CLAIMS = ['exp', 'iat', 'sub']  # Required claims
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:aswin@localhost:5432/donornearme'
    )
    
    # Security settings
    BCRYPT_LOG_ROUNDS = 12
    
    # API settings
    API_TITLE = 'Donor Near Me API'
    API_VERSION = 'v1'
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://postgres:aswin@localhost:5432/donor_near_me_test'
    )

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
