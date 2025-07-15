from flask import Flask, jsonify, request, session
from flask_cors import CORS
from config import Config
from db import db
from utils.jwt_handler import jwt
from flask_jwt_extended import jwt_required
from routes.auth_routes import auth_bp
from routes.blood_routes import blood_bp
from routes.hospital_routes import hospital_bp
import psycopg2
from werkzeug.security import check_password_hash

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    
    # Updated CORS configuration - more permissive for development
    CORS(
        app,
        origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"]
    )
    
    print("✅ CORS configured for origins:", ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"])

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(blood_bp, url_prefix='/blood')
    app.register_blueprint(hospital_bp, url_prefix='/hospital')

    # Root-level route for /blood-requests (alias for /blood/request)
    @app.route('/blood-requests', methods=['POST'])
    @jwt_required()
    def blood_requests_alias():
        """Root-level alias for /blood/request to support frontend"""
        from routes.blood_routes import create_blood_request
        return create_blood_request()
    
    # Root-level route for /blood-request-responses (alias for /blood/request/{id}/respond)
    @app.route('/blood-request-responses', methods=['POST'])
    @jwt_required()
    def blood_request_responses_alias():
        """Root-level alias for /blood/request/{id}/respond to support frontend"""
        from routes.blood_routes import respond_to_blood_request
        data = request.get_json()
        if not data or 'requestId' not in data:
            return jsonify({'error': 'Missing requestId in payload'}), 400
        
        # Extract requestId from payload and call the respond function
        request_id = data['requestId']
        return respond_to_blood_request(request_id)

    @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def catch_all(path):
        return jsonify({'error': f'Route /{path} not found'}), 404

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
