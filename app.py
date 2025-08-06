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

    # 🔧 Enhanced JWT error handlers with better debugging
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"[JWT] Token expired for user: {jwt_payload.get('sub')}")
        return jsonify({'status': 'error', 'message': 'Token has expired'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"[JWT] Invalid token: {error}")
        if "Subject must be a string" in str(error):
            return jsonify({
                'status': 'error', 
                'message': 'Invalid token: Please log out and log in again to get a fresh token'
            }), 401
        return jsonify({'status': 'error', 'message': 'Invalid token'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"[JWT] Unauthorized: {error}")
        return jsonify({'status': 'error', 'message': 'Authorization token is missing'}), 401

    # 🔧 Add token verification handlers
    @jwt.token_verification_failed_loader
    def token_verification_failed_callback(jwt_header, jwt_payload):
        print(f"[JWT] Token verification failed: user_id={jwt_payload.get('sub')}")
        return jsonify({'status': 'error', 'message': 'Token verification failed'}), 401
    
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

    # Test endpoint for database connectivity without authentication
    @app.route('/blood/request/test', methods=['POST'])
    def test_blood_request():
        """Test endpoint for blood request creation without authentication"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            print(f"Test endpoint received data: {data}")
            
            # Import models
            from models.lookup import LookupBloodGroup
            from models.blood_request import BloodRequest
            from datetime import datetime
            
            # Get or create blood groups
            blood_groups = LookupBloodGroup.query.all()
            if blood_groups:
                valid_blood_group_id = blood_groups[0].blood_group_id
                print(f"Using existing blood group ID: {valid_blood_group_id}")
            else:
                # Create O+ blood group if none exist
                new_blood_group = LookupBloodGroup(
                    blood_group_name='O+',
                    from_date=datetime.now().date()
                )
                db.session.add(new_blood_group)
                db.session.flush()
                valid_blood_group_id = new_blood_group.blood_group_id
                print(f"Created new blood group O+ with ID: {valid_blood_group_id}")
            
            # Create blood request
            blood_request = BloodRequest(
                hospital_id=data['hospital_id'],
                blood_group_type=valid_blood_group_id,
                no_of_units=data['no_of_units'],
                patient_name=data['patient_name'],
                patient_contact_email=data['patient_contact_email'],
                patient_contact_phone_number=data['patient_contact_phone_number'],
                required_by_date=datetime.strptime(data['required_by_date'], '%Y-%m-%d').date(),
                description=data['description'],
                status=data['status'],
                from_date=datetime.strptime(data['from_date'], '%Y-%m-%d').date(),
                to_date=datetime.strptime(data['to_date'], '%Y-%m-%d').date() if data.get('to_date') else None,
                user_id=36
            )
            
            db.session.add(blood_request)
            db.session.commit()
            
            print(f"✅ Successfully created blood request with ID: {blood_request.blood_request_id}")
            
            return jsonify({
                "success": True,
                "blood_request_id": blood_request.blood_request_id,
                "message": "Test blood request created successfully",
                "data": {
                    "id": blood_request.blood_request_id,
                    "patient_name": blood_request.patient_name,
                    "blood_group_type": blood_request.blood_group_type,
                    "hospital_id": blood_request.hospital_id,
                    "status": blood_request.status,
                    "user_id": blood_request.user_id
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Test endpoint error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": f"Failed to create test blood request: {str(e)}",
                "success": False
            }), 500

    # Additional test endpoint variations
    @app.route('/api/blood/request/test', methods=['POST'])
    def test_blood_request_api():
        """API version of test endpoint"""
        return test_blood_request()

    @app.route('/test/blood/request', methods=['POST'])
    def test_blood_request_alt():
        """Alternative test endpoint"""
        return test_blood_request()

    @app.route('/api/test/blood/request', methods=['POST'])
    def test_blood_request_alt_api():
        """Alternative API test endpoint"""
        return test_blood_request()

    # Database connectivity test endpoint
    @app.route('/test/db', methods=['GET'])
    def test_database():
        """Test database connection"""
        try:
            from models.blood_request import BloodRequest
            from models.hospital import Hospital
            from models.lookup import LookupBloodGroup
            
            # Test database queries
            total_requests = BloodRequest.query.count()
            total_hospitals = Hospital.query.count()
            total_blood_groups = LookupBloodGroup.query.count()
            
            return jsonify({
                'success': True,
                'message': 'Database connection successful',
                'data': {
                    'total_blood_requests': total_requests,
                    'total_hospitals': total_hospitals,
                    'total_blood_groups': total_blood_groups
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Database connection failed: {str(e)}'
            }), 500

    @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def catch_all(path):
        return jsonify({'error': f'Route /{path} not found'}), 404

    # Add a debug endpoint to test manual form submission without full authentication
    @app.route('/blood/request/debug', methods=['POST'])
    def debug_blood_request():
        """Debug endpoint to test manual form submission"""
        try:
            print("\n" + "="*50)
            print("DEBUG BLOOD REQUEST ENDPOINT CALLED")
            print("="*50)
            
            data = request.get_json()
            print(f"[DEBUG] Received data: {data}")
            print(f"[DEBUG] Headers: {dict(request.headers)}")
            
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Check if this looks like manual form data vs test data
            if 'patient_name' in data and 'hospital_id' in data:
                print("[DEBUG] This appears to be manual form data")
                
                # Import models
                from models.lookup import LookupBloodGroup
                from models.blood_request import BloodRequest
                from datetime import datetime
                
                # Handle blood group conversion - check what exists in database
                blood_group_type = data.get('blood_group_type')
                print(f"[DEBUG] Blood group type: {blood_group_type} (type: {type(blood_group_type)})")
                
                # Check what blood groups exist in database
                existing_blood_groups = LookupBloodGroup.query.all()
                print(f"[DEBUG] Existing blood groups: {[(bg.blood_group_id, bg.blood_group_name) for bg in existing_blood_groups]}")
                
                valid_blood_group_id = None
                
                if isinstance(blood_group_type, int):
                    # Check if this ID exists
                    bg = LookupBloodGroup.query.get(blood_group_type)
                    if bg:
                        valid_blood_group_id = blood_group_type
                        print(f"[DEBUG] Found existing blood group ID: {valid_blood_group_id}")
                    else:
                        print(f"[DEBUG] Blood group ID {blood_group_type} doesn't exist, will create or use existing")
                
                # If we don't have a valid ID yet, try to find or create blood groups
                if valid_blood_group_id is None:
                    if existing_blood_groups:
                        # Use the first existing blood group
                        valid_blood_group_id = existing_blood_groups[0].blood_group_id
                        print(f"[DEBUG] Using first existing blood group ID: {valid_blood_group_id}")
                    else:
                        # Create the standard blood groups
                        print("[DEBUG] No blood groups exist, creating them...")
                        blood_groups_to_create = [
                            {'name': 'A+', 'id': 1},
                            {'name': 'A-', 'id': 2},
                            {'name': 'B+', 'id': 3},
                            {'name': 'B-', 'id': 4},
                            {'name': 'AB+', 'id': 5},
                            {'name': 'AB-', 'id': 6},
                            {'name': 'O+', 'id': 7},
                            {'name': 'O-', 'id': 8}
                        ]
                        
                        for bg_data in blood_groups_to_create:
                            new_bg = LookupBloodGroup(
                                blood_group_name=bg_data['name'],
                                from_date=datetime.now().date()
                            )
                            db.session.add(new_bg)
                            db.session.flush()  # Get the auto-generated ID
                            print(f"[DEBUG] Created blood group {bg_data['name']} with ID: {new_bg.blood_group_id}")
                        
                        db.session.commit()
                        
                        # Now use the O+ blood group (which should be ID 7 if created in order)
                        o_plus = LookupBloodGroup.query.filter_by(blood_group_name='O+').first()
                        if o_plus:
                            valid_blood_group_id = o_plus.blood_group_id
                            print(f"[DEBUG] Using newly created O+ blood group ID: {valid_blood_group_id}")
                        else:
                            # Fallback to first available
                            first_bg = LookupBloodGroup.query.first()
                            valid_blood_group_id = first_bg.blood_group_id if first_bg else 1
                            print(f"[DEBUG] Fallback to first blood group ID: {valid_blood_group_id}")
                
                print(f"[DEBUG] Final blood group ID to use: {valid_blood_group_id}")
                
                # Convert hospital_id to integer if it's a string
                hospital_id = data['hospital_id']
                if isinstance(hospital_id, str):
                    hospital_id = int(hospital_id)
                print(f"[DEBUG] Hospital ID: {hospital_id}")
                
                # Create blood request with user_id 36 (same as test)
                blood_request = BloodRequest(
                    hospital_id=hospital_id,
                    blood_group_type=valid_blood_group_id,
                    no_of_units=data['no_of_units'],
                    patient_name=data['patient_name'],
                    patient_contact_email=data['patient_contact_email'],
                    patient_contact_phone_number=data['patient_contact_phone_number'],
                    required_by_date=datetime.strptime(data['required_by_date'], '%Y-%m-%d').date(),
                    description=data['description'],
                    status=data.get('status', 'pending'),
                    from_date=datetime.strptime(data['from_date'], '%Y-%m-%d').date() if data.get('from_date') else datetime.now().date(),
                    to_date=datetime.strptime(data['to_date'], '%Y-%m-%d').date() if data.get('to_date') else None,
                    user_id=36
                )
                
                db.session.add(blood_request)
                db.session.commit()
                
                print(f"✅ Successfully created debug blood request with ID: {blood_request.blood_request_id}")
                
                return jsonify({
                    "success": True,
                    "blood_request_id": blood_request.blood_request_id,
                    "message": "Debug blood request created successfully",
                    "data": {
                        "id": blood_request.blood_request_id,
                        "patient_name": blood_request.patient_name,
                        "blood_group_type": blood_request.blood_group_type,
                        "hospital_id": blood_request.hospital_id,
                        "status": blood_request.status,
                        "user_id": blood_request.user_id
                    }
                }), 201
            else:
                return jsonify({"error": "Invalid form data structure"}), 400
                
        except Exception as e:
            db.session.rollback()
            print(f"Debug endpoint error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": f"Failed to create debug blood request: {str(e)}",
                "success": False
            }), 500
        finally:
            print("="*50)
            print("DEBUG BLOOD REQUEST ENDPOINT FINISHED")
            print("="*50 + "\n")

    # Add a non-authenticated version of the blood request endpoint for development
    @app.route('/blood/request/no-auth', methods=['POST'])
    def create_blood_request_no_auth():
        """Create blood request without authentication (for development/testing)"""
        try:
            print("\n" + "="*50)
            print("NO-AUTH BLOOD REQUEST ENDPOINT CALLED")
            print("="*50)
            
            data = request.get_json()
            print(f"[NO-AUTH] Received data: {data}")
            
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Import models
            from models.lookup import LookupBloodGroup
            from models.blood_request import BloodRequest
            from models.hospital import Hospital
            from datetime import datetime
            
            # Validate hospital exists
            hospital_id = int(data['hospital_id']) if isinstance(data['hospital_id'], str) else data['hospital_id']
            hospital_obj = Hospital.query.get(hospital_id)
            if not hospital_obj:
                return jsonify({'error': f'Hospital with ID {hospital_id} not found'}), 404
            
            # Handle blood group - same logic as debug endpoint
            blood_group_type = data.get('blood_group_type')
            valid_blood_group_id = None
            
            if isinstance(blood_group_type, int):
                bg = LookupBloodGroup.query.get(blood_group_type)
                if bg:
                    valid_blood_group_id = blood_group_type
                else:
                    # Use first available
                    first_bg = LookupBloodGroup.query.first()
                    valid_blood_group_id = first_bg.blood_group_id if first_bg else 1
            else:
                # Get first available blood group
                first_bg = LookupBloodGroup.query.first()
                valid_blood_group_id = first_bg.blood_group_id if first_bg else 1
            
            print(f"[NO-AUTH] Using blood group ID: {valid_blood_group_id}")
            
            # Create blood request (using user_id 36 like the test endpoints)
            blood_request = BloodRequest(
                hospital_id=hospital_id,
                blood_group_type=valid_blood_group_id,
                no_of_units=data['no_of_units'],
                patient_name=data['patient_name'],
                patient_contact_email=data['patient_contact_email'],
                patient_contact_phone_number=data['patient_contact_phone_number'],
                required_by_date=datetime.strptime(data['required_by_date'], '%Y-%m-%d').date(),
                description=data['description'],
                status=data.get('status', 'pending'),
                from_date=datetime.strptime(data['from_date'], '%Y-%m-%d').date() if data.get('from_date') else datetime.now().date(),
                to_date=datetime.strptime(data['to_date'], '%Y-%m-%d').date() if data.get('to_date') else None,
                user_id=36
            )
            
            db.session.add(blood_request)
            db.session.commit()
            
            print(f"✅ Successfully created no-auth blood request with ID: {blood_request.blood_request_id}")
            
            # Return response in same format as authenticated endpoint
            return jsonify({
                'success': True,
                'message': 'Blood request created successfully',
                'blood_request_id': blood_request.blood_request_id,
                'data': {
                    'id': blood_request.blood_request_id,
                    'patient_name': blood_request.patient_name,
                    'hospital_id': blood_request.hospital_id,
                    'status': blood_request.status,
                    'user_id': blood_request.user_id
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"No-auth endpoint error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": f"Failed to create blood request: {str(e)}",
                "success": False
            }), 500
        finally:
            print("="*50)
            print("NO-AUTH BLOOD REQUEST ENDPOINT FINISHED")
            print("="*50 + "\n")

    # Add a simple non-auth version that works exactly like the debug endpoint
    @app.route('/blood/request/simple', methods=['POST'])
    def create_blood_request_simple():
        """Simple blood request creation - same as debug but cleaner name"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            print(f"[SIMPLE] Creating blood request: {data}")
            
            # Import models
            from models.lookup import LookupBloodGroup
            from models.blood_request import BloodRequest
            from models.hospital import Hospital
            from datetime import datetime
            
            # Validate hospital exists
            hospital_id = int(data['hospital_id']) if isinstance(data['hospital_id'], str) else data['hospital_id']
            hospital_obj = Hospital.query.get(hospital_id)
            if not hospital_obj:
                return jsonify({'error': f'Hospital with ID {hospital_id} not found'}), 404
            
            # Handle blood group - use first available if invalid ID provided
            blood_group_type = data.get('blood_group_type')
            existing_blood_groups = LookupBloodGroup.query.all()
            
            if isinstance(blood_group_type, int) and LookupBloodGroup.query.get(blood_group_type):
                valid_blood_group_id = blood_group_type
            else:
                # Use first available blood group or create if none exist
                if existing_blood_groups:
                    valid_blood_group_id = existing_blood_groups[0].blood_group_id
                else:
                    # Create O+ if none exist
                    new_bg = LookupBloodGroup(
                        blood_group_name='O+',
                        from_date=datetime.now().date()
                    )
                    db.session.add(new_bg)
                    db.session.flush()
                    valid_blood_group_id = new_bg.blood_group_id
            
            print(f"[SIMPLE] Using blood group ID: {valid_blood_group_id}")
            
            # Create blood request
            blood_request = BloodRequest(
                hospital_id=hospital_id,
                blood_group_type=valid_blood_group_id,
                no_of_units=data['no_of_units'],
                patient_name=data['patient_name'],
                patient_contact_email=data['patient_contact_email'],
                patient_contact_phone_number=data['patient_contact_phone_number'],
                required_by_date=datetime.strptime(data['required_by_date'], '%Y-%m-%d').date(),
                description=data['description'],
                status=data.get('status', 'pending'),
                from_date=datetime.strptime(data['from_date'], '%Y-%m-%d').date() if data.get('from_date') else datetime.now().date(),
                to_date=datetime.strptime(data['to_date'], '%Y-%m-%d').date() if data.get('to_date') else None,
                user_id=36  # Use fixed user ID like test endpoints
            )
            
            db.session.add(blood_request)
            db.session.commit()
            
            print(f"✅ Successfully created simple blood request with ID: {blood_request.blood_request_id}")
            
            # Return in standard format
            return jsonify({
                'success': True,
                'message': 'Blood request created successfully',
                'blood_request_id': blood_request.blood_request_id,
                'data': {
                    'id': blood_request.blood_request_id,
                    'patient_name': blood_request.patient_name,
                    'hospital_id': blood_request.hospital_id,
                    'status': blood_request.status,
                    'user_id': blood_request.user_id
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Simple endpoint error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": f"Failed to create blood request: {str(e)}",
                "success": False
            }), 500

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
    
    print("🚀 Starting Flask server on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
