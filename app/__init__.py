from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from config import config
from models import db
from app.utils.jwt_handler import jwt

def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate = Migrate(app, db)
    
    # Configure CORS
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.hospital_routes import hospital_bp
    from app.routes.blood_routes import blood_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(hospital_bp, url_prefix='/hospital')
    app.register_blueprint(blood_bp, url_prefix='/blood')
    
    # Root-level routes for frontend compatibility
    @app.route('/blood-requests', methods=['POST'])
    def blood_requests_alias():
        """Root-level alias for /blood/request"""
        from app.routes.blood_routes import create_blood_request
        return create_blood_request()
    
    @app.route('/blood-request-responses', methods=['POST'])
    def blood_request_responses_alias():
        """Root-level alias for /blood/request/{id}/respond"""
        from app.routes.blood_routes import respond_to_blood_request
        from flask import request, jsonify
        
        data = request.get_json()
        if not data or 'requestId' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing requestId in payload'
            }), 400
        
        request_id = data['requestId']
        return respond_to_blood_request(request_id)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {
            'status': 'error',
            'message': 'Route not found'
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {
            'status': 'error',
            'message': 'Internal server error'
        }, 500
    
    return app 