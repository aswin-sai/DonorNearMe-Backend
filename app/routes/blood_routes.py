from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, BloodRequest, BloodRequestResponse, User, Hospital, LookupBloodGroup, UserHospitalAdminLineage
from app.schemas.blood_request_schemas import BloodRequestSchema, BloodRequestResponseSchema
from marshmallow import ValidationError
from datetime import datetime, date
from sqlalchemy import and_

blood_bp = Blueprint('blood', __name__)

# Initialize schemas
blood_request_schema = BloodRequestSchema()
blood_request_response_schema = BloodRequestResponseSchema()

# Create a new blood request
@blood_bp.route('/request', methods=['POST'])
@jwt_required()
def create_blood_request():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        # Validate input data using Marshmallow schema
        try:
            validated_data = blood_request_schema.load(data)
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Get hospital_id from request body (required for all users)
        try:
            hospital_id = int(validated_data['hospital_id'])
        except (ValueError, TypeError, KeyError):
            return jsonify({'error': 'Invalid or missing hospital_id'}), 400
        
        # Validate hospital exists
        hospital_obj = Hospital.query.get(hospital_id)
        if not hospital_obj:
            available_hospitals = Hospital.query.all()
            hospital_names = [h.hospital_name for h in available_hospitals]
            return jsonify({
                'error': f'Hospital with ID {hospital_id} not found. Available hospitals: {", ".join(hospital_names)}'
            }), 404
        
        # Handle blood group type (can be string or integer)
        blood_group_type = validated_data['blood_group_type']
        blood_group_id = None
        
        if isinstance(blood_group_type, int):
            # If it's already an integer, use it directly
            blood_group_id = blood_group_type
        else:
            # If it's a string, look up the blood group by name
            blood_group = LookupBloodGroup.query.filter(
                LookupBloodGroup.blood_group_name.ilike(str(blood_group_type))
            ).first()
            if blood_group:
                blood_group_id = blood_group.blood_group_id
            else:
                # Get available blood groups for better error message
                available_blood_groups = LookupBloodGroup.query.all()
                blood_group_names = [bg.blood_group_name for bg in available_blood_groups]
                return jsonify({
                    'error': f'Blood group "{blood_group_type}" not found. Available blood groups: {", ".join(blood_group_names)}'
                }), 404
        
        # Validate blood group exists
        blood_group = LookupBloodGroup.query.get(blood_group_id)
        if not blood_group:
            available_blood_groups = LookupBloodGroup.query.all()
            blood_group_names = [bg.blood_group_name for bg in available_blood_groups]
            return jsonify({
                'error': f'Blood group with ID {blood_group_id} not found. Available blood groups: {", ".join(blood_group_names)}'
            }), 404
        
        # Normalize status to lowercase
        status = validated_data.get('status', 'pending').lower()
        if status not in ['pending', 'accepted', 'cancelled', 'completed']:
            status = 'pending'
        
        # Create the blood request
        blood_request = BloodRequest(
            user_id=current_user_id,
            hospital_id=hospital_id,
            blood_group_type=blood_group_id,
            no_of_units=validated_data['no_of_units'],
            patient_name=validated_data['patient_name'],
            patient_contact_email=validated_data.get('patient_contact_email'),
            patient_contact_phone_number=validated_data.get('patient_contact_phone_number'),
            required_by_date=validated_data.get('required_by_date'),
            description=validated_data.get('description'),
            status=status,
            from_date=date.today()
        )
        
        db.session.add(blood_request)
        db.session.commit()
        
        return jsonify({
            'message': 'Blood request created successfully',
            'blood_request_id': blood_request.blood_request_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create blood request: {str(e)}'}), 500

# Alias endpoint for /blood-requests (to support frontend)
@blood_bp.route('/blood-requests', methods=['POST'])
@jwt_required()
def create_blood_request_alias():
    """Alias endpoint for /blood/request to support frontend compatibility"""
    return create_blood_request()

# Get all blood requests (with optional filters)
@blood_bp.route('/requests', methods=['GET'])
def get_blood_requests():
    try:
        # Try to get current user ID, but don't require authentication
        current_user_id = None
        try:
            current_user_id = get_jwt_identity()
        except:
            # If no valid token, continue without user filtering
            pass
        
        # Get query parameters for filtering
        status = request.args.get('status')
        blood_group_id = request.args.get('blood_group_id')
        hospital_id = request.args.get('hospital_id')
        user_id = request.args.get('user_id')
        
        # Build query
        query = BloodRequest.query
        
        # Apply filters
        if status:
            query = query.filter(BloodRequest.status == status)
        if blood_group_id:
            query = query.filter(BloodRequest.blood_group_type == blood_group_id)
        if hospital_id:
            query = query.filter(BloodRequest.hospital_id == hospital_id)
        if user_id:
            query = query.filter(BloodRequest.user_id == user_id)
        
        # If authenticated, show all requests. If not, show only public info
        if current_user_id:
            # Get results with relationships for authenticated users
            requests = query.join(User).join(Hospital).join(LookupBloodGroup, BloodRequest.blood_group_type == LookupBloodGroup.blood_group_id).all()
            
            result = []
            for req in requests:
                result.append({
                    'blood_request_id': req.blood_request_id,
                    'user_id': req.user_id,
                    'user_name': req.user.user_name,
                    'hospital_id': req.hospital_id,
                    'hospital_name': req.hospital.hospital_name,
                    'blood_group_type': req.blood_group_type,
                    'blood_group_name': req.blood_group.blood_group_name,
                    'no_of_units': req.no_of_units,
                    'patient_name': req.patient_name,
                    'patient_contact_email': req.patient_contact_email,
                    'patient_contact_phone_number': req.patient_contact_phone_number,
                    'required_by_date': req.required_by_date.isoformat() if req.required_by_date else None,
                    'description': req.description,
                    'status': req.status,
                    'from_date': req.from_date.isoformat() if req.from_date else None,
                    'to_date': req.to_date.isoformat() if req.to_date else None,
                    'created_at': req.created_at.isoformat() if req.created_at else None,
                    'updated_at': req.updated_at.isoformat() if req.updated_at else None
                })
        else:
            # For unauthenticated users, show limited information
            requests = query.join(Hospital).join(LookupBloodGroup, BloodRequest.blood_group_type == LookupBloodGroup.blood_group_id).all()
            
            result = []
            for req in requests:
                result.append({
                    'blood_request_id': req.blood_request_id,
                    'hospital_id': req.hospital_id,
                    'hospital_name': req.hospital.hospital_name,
                    'blood_group_type': req.blood_group_type,
                    'blood_group_name': req.blood_group.blood_group_name,
                    'no_of_units': req.no_of_units,
                    'required_by_date': req.required_by_date.isoformat() if req.required_by_date else None,
                    'description': req.description,
                    'status': req.status,
                    'from_date': req.from_date.isoformat() if req.from_date else None,
                    'created_at': req.created_at.isoformat() if req.created_at else None
                })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get a specific blood request by ID
@blood_bp.route('/request/<int:request_id>', methods=['GET'])
@jwt_required()
def get_blood_request(request_id):
    try:
        request_obj = BloodRequest.query.filter(
            BloodRequest.blood_request_id == request_id
        ).join(User).join(Hospital).join(LookupBloodGroup).first()
        
        if not request_obj:
            return jsonify({'error': 'Blood request not found'}), 404
        
        result = {
            'blood_request_id': request_obj.blood_request_id,
            'user_id': request_obj.user_id,
            'user_name': request_obj.user.user_name,
            'hospital_id': request_obj.hospital_id,
            'hospital_name': request_obj.hospital.hospital_name,
            'blood_group_type': request_obj.blood_group_type,
            'blood_group_name': request_obj.blood_group.blood_group_name,
            'no_of_units': request_obj.no_of_units,
            'patient_name': request_obj.patient_name,
            'patient_contact_email': request_obj.patient_contact_email,
            'patient_contact_phone_number': request_obj.patient_contact_phone_number,
            'required_by_date': request_obj.required_by_date.isoformat() if request_obj.required_by_date else None,
            'description': request_obj.description,
            'status': request_obj.status,
            'from_date': request_obj.from_date.isoformat() if request_obj.from_date else None,
            'to_date': request_obj.to_date.isoformat() if request_obj.to_date else None,
            'created_at': request_obj.created_at.isoformat() if request_obj.created_at else None,
            'updated_at': request_obj.updated_at.isoformat() if request_obj.updated_at else None,
            'responses': []
        }
        
        # Get responses for this request
        responses = BloodRequestResponse.query.filter(
            BloodRequestResponse.blood_request_id == request_id
        ).join(User).all()
        
        for response in responses:
            result['responses'].append({
                'blood_requests_response_id': response.blood_requests_response_id,
                'user_id': response.user_id,
                'user_name': response.user.user_name,
                'response_status': response.response_status,
                'message': response.message,
                'from_date': response.from_date.isoformat() if response.from_date else None,
                'responded_date': response.responded_date.isoformat() if response.responded_date else None,
                'to_date': response.to_date.isoformat() if response.to_date else None,
                'created_at': response.created_at.isoformat() if response.created_at else None
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update a blood request
@blood_bp.route('/request/<int:request_id>', methods=['PUT'])
@jwt_required()
def update_blood_request(request_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Find the blood request
        request_obj = BloodRequest.query.get(request_id)
        if not request_obj:
            return jsonify({'error': 'Blood request not found'}), 404
        
        # Check if user owns the request or is admin
        if request_obj.user_id != current_user_id:
            # TODO: Add admin role check here
            return jsonify({'error': 'Unauthorized to update this request'}), 403
        
        # Validate input data
        try:
            validated_data = blood_request_schema.load(data, partial=True)
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Update fields
        updateable_fields = [
            'no_of_units', 'patient_name', 'patient_contact_email', 
            'patient_contact_phone_number', 'required_by_date', 'description', 'status'
        ]
        
        for field in updateable_fields:
            if field in validated_data:
                setattr(request_obj, field, validated_data[field])
        
        db.session.commit()
        
        return jsonify({'message': 'Blood request updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete a blood request
@blood_bp.route('/request/<int:request_id>', methods=['DELETE'])
@jwt_required()
def delete_blood_request(request_id):
    try:
        current_user_id = get_jwt_identity()
        
        # Find the blood request
        request_obj = BloodRequest.query.get(request_id)
        if not request_obj:
            return jsonify({'error': 'Blood request not found'}), 404
        
        # Check if user owns the request or is admin
        if request_obj.user_id != current_user_id:
            # TODO: Add admin role check here
            return jsonify({'error': 'Unauthorized to delete this request'}), 403
        
        # Soft delete by setting to_date
        request_obj.to_date = date.today()
        request_obj.status = 'cancelled'
        
        db.session.commit()
        
        return jsonify({'message': 'Blood request cancelled successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Respond to a blood request
@blood_bp.route('/request/<int:request_id>/respond', methods=['POST'])
@jwt_required()
def respond_to_blood_request(request_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate input data
        try:
            validated_data = blood_request_response_schema.load(data)
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Find the blood request
        request_obj = BloodRequest.query.get(request_id)
        if not request_obj:
            return jsonify({'error': 'Blood request not found'}), 404
        
        # Check if user is not the request creator
        if request_obj.user_id == current_user_id:
            return jsonify({'error': 'Cannot respond to your own request'}), 400
        
        # Check if user already responded
        existing_response = BloodRequestResponse.query.filter(
            and_(
                BloodRequestResponse.blood_request_id == request_id,
                BloodRequestResponse.user_id == current_user_id
            )
        ).first()
        
        if existing_response:
            return jsonify({'error': 'You have already responded to this request'}), 400
        
        # Create response with all required fields
        response = BloodRequestResponse(
            blood_request_id=request_id,
            user_id=current_user_id,
            response_status=validated_data['response_status'],
            message=validated_data.get('message'),
            from_date=date.today(),
            responded_date=date.today(),
            to_date=None,  # Will be set when response is completed/cancelled
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.session.add(response)
        
        # Update request status based on response
        if validated_data['response_status'] == 'accepted':
            request_obj.status = 'accepted'
        elif validated_data['response_status'] == 'declined':
            # Keep request as pending if declined, so others can still respond
            pass
        
        db.session.commit()
        
        return jsonify({
            'message': 'Response submitted successfully',
            'response_id': response.blood_requests_response_id,
            'response_status': response.response_status,
            'blood_request_id': request_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to submit response: {str(e)}'}), 500

# Get blood requests by current user
@blood_bp.route('/my-requests', methods=['GET'])
@jwt_required()
def get_my_blood_requests():
    try:
        current_user_id = get_jwt_identity()
        
        requests = BloodRequest.query.filter(
            BloodRequest.user_id == current_user_id
        ).join(Hospital).join(LookupBloodGroup).all()
        
        result = []
        for req in requests:
            result.append({
                'blood_request_id': req.blood_request_id,
                'hospital_name': req.hospital.hospital_name,
                'blood_group_name': req.blood_group.blood_group_name,
                'no_of_units': req.no_of_units,
                'patient_name': req.patient_name,
                'required_by_date': req.required_by_date.isoformat() if req.required_by_date else None,
                'status': req.status,
                'created_at': req.created_at.isoformat() if req.created_at else None
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get responses by current user
@blood_bp.route('/my-responses', methods=['GET'])
@jwt_required()
def get_my_responses():
    try:
        current_user_id = get_jwt_identity()
        
        # Get all responses by the current user
        responses = BloodRequestResponse.query.filter(
            BloodRequestResponse.user_id == current_user_id
        ).join(BloodRequest).join(Hospital).join(LookupBloodGroup).all()
        
        result = []
        for response in responses:
            result.append({
                'blood_requests_response_id': response.blood_requests_response_id,
                'blood_request_id': response.blood_request_id,
                'response_status': response.response_status,
                'message': response.message,
                'from_date': response.from_date.isoformat() if response.from_date else None,
                'responded_date': response.responded_date.isoformat() if response.responded_date else None,
                'to_date': response.to_date.isoformat() if response.to_date else None,
                'created_at': response.created_at.isoformat() if response.created_at else None,
                'updated_at': response.updated_at.isoformat() if response.updated_at else None,
                # Blood request details
                'blood_request': {
                    'hospital_name': response.blood_request.hospital.hospital_name,
                    'blood_group_name': response.blood_request.blood_group.blood_group_name,
                    'no_of_units': response.blood_request.no_of_units,
                    'patient_name': response.blood_request.patient_name,
                    'required_by_date': response.blood_request.required_by_date.isoformat() if response.blood_request.required_by_date else None,
                    'status': response.blood_request.status,
                    'description': response.blood_request.description
                }
            })
        
        return jsonify({
            'total_responses': len(result),
            'responses': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get responses: {str(e)}'}), 500

# Get available blood groups
@blood_bp.route('/blood-groups', methods=['GET'])
def get_blood_groups():
    try:
        blood_groups = LookupBloodGroup.query.all()
        result = [
            {
                'blood_group_id': bg.blood_group_id,
                'blood_group_name': bg.blood_group_name
            } for bg in blood_groups
        ]
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get responses for a specific blood request
@blood_bp.route('/request/<int:request_id>/responses', methods=['GET'])
def get_blood_request_responses(request_id):
    try:
        # Find the blood request
        request_obj = BloodRequest.query.get(request_id)
        if not request_obj:
            return jsonify({'error': 'Blood request not found'}), 404
        
        # Get all responses for this request
        responses = BloodRequestResponse.query.filter(
            BloodRequestResponse.blood_request_id == request_id
        ).join(User).all()
        
        result = []
        for response in responses:
            result.append({
                'blood_requests_response_id': response.blood_requests_response_id,
                'blood_request_id': response.blood_request_id,
                'user_id': response.user_id,
                'user_name': response.user.user_name,
                'response_status': response.response_status,
                'message': response.message,
                'from_date': response.from_date.isoformat() if response.from_date else None,
                'responded_date': response.responded_date.isoformat() if response.responded_date else None,
                'to_date': response.to_date.isoformat() if response.to_date else None,
                'created_at': response.created_at.isoformat() if response.created_at else None,
                'updated_at': response.updated_at.isoformat() if response.updated_at else None
            })
        
        return jsonify({
            'blood_request_id': request_id,
            'total_responses': len(result),
            'responses': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get responses: {str(e)}'}), 500

@blood_bp.route('/donation', methods=['POST'])
@jwt_required()
def create_donation():
    """Create a donation (alias for schedule_donation to match frontend expectations)."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if this is blood request creation data (has patient_contact_email, hospital_id, etc.)
        # or donation scheduling data (has request_id, scheduled_datetime, etc.)
        if 'patient_contact_email' in data or 'hospital_id' in data:
            # This is blood request creation data - redirect to blood request creation
            return create_blood_request()
        else:
            # This is donation scheduling data - handle as donation
            return schedule_donation()
            
    except Exception as e:
        return jsonify({'error': f'Failed to process donation: {str(e)}'}), 500

@blood_bp.route('/donation/schedule', methods=['POST'])
@jwt_required()
def schedule_donation():
    """Schedule a donation for a blood request."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Handle different possible field names from frontend
        request_id = data.get('request_id') or data.get('blood_request_id') or data.get('bloodRequestId')
        scheduled_datetime = data.get('scheduled_datetime') or data.get('scheduled_date') or data.get('scheduledDate')
        message = data.get('message') or data.get('notes') or data.get('description')
        
        if not request_id:
            return jsonify({'error': 'request_id or blood_request_id is required'}), 400
        if not scheduled_datetime:
            return jsonify({'error': 'scheduled_datetime or scheduled_date is required'}), 400
        
        # Handle mock request IDs (development mode)
        if isinstance(request_id, str) and request_id.startswith('mock-'):
            return jsonify({
                'message': 'Donation scheduled successfully (development mode)',
                'response_id': f'mock-response-{int(datetime.now().timestamp())}',
                'development_mode': True
            }), 201
        
        # Convert request_id to integer if it's a string
        try:
            if isinstance(request_id, str):
                request_id = int(request_id)
        except ValueError:
            return jsonify({'error': f'Invalid request_id format: {request_id}. Must be a valid integer.'}), 400
        
        # Validate the blood request exists
        blood_request = BloodRequest.query.get(request_id)
        if not blood_request:
            return jsonify({'error': f'Blood request with ID {request_id} not found'}), 404
        
        # Check if user is not the request creator
        if blood_request.user_id == current_user_id:
            return jsonify({'error': 'Cannot respond to your own request'}), 400
        
        # Check if user has already responded to this request
        existing_response = BloodRequestResponse.query.filter_by(
            blood_request_id=request_id,
            user_id=current_user_id
        ).first()
        
        if existing_response:
            # Update existing response
            existing_response.scheduled_datetime = scheduled_datetime
            existing_response.message = message
            existing_response.response_status = 'scheduled'
            existing_response.updated_date = datetime.now()
            db.session.commit()
            
            return jsonify({
                'message': 'Donation schedule updated successfully',
                'response_id': existing_response.blood_requests_response_id
            }), 200
        else:
            # Create new response
            response = BloodRequestResponse(
                blood_request_id=request_id,
                user_id=current_user_id,
                response_status='scheduled',
                scheduled_datetime=scheduled_datetime,
                message=message,
                from_date=date.today(),
                created_date=datetime.now(),
                updated_date=datetime.now()
            )
            
            db.session.add(response)
            db.session.commit()
            
            return jsonify({
                'message': 'Donation scheduled successfully',
                'response_id': response.blood_requests_response_id
            }), 201
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to schedule donation: {str(e)}'}), 500

@blood_bp.route('/donations/my', methods=['GET'])
@jwt_required()
def get_my_scheduled_donations():
    """Get all scheduled donations for the current user."""
    try:
        current_user_id = get_jwt_identity()
        responses = BloodRequestResponse.query.filter(
            BloodRequestResponse.user_id == current_user_id,
            BloodRequestResponse.scheduled_datetime != None
        ).join(BloodRequest).join(Hospital).join(LookupBloodGroup).all()
        result = []
        for response in responses:
            req = response.blood_request
            result.append({
                'blood_requests_response_id': response.blood_requests_response_id,
                'blood_request_id': response.blood_request_id,
                'scheduled_datetime': response.scheduled_datetime.isoformat() if response.scheduled_datetime else None,
                'response_status': response.response_status,
                'message': response.message,
                'from_date': response.from_date.isoformat() if response.from_date else None,
                'responded_date': response.responded_date.isoformat() if response.responded_date else None,
                'to_date': response.to_date.isoformat() if response.to_date else None,
                'created_at': response.created_at.isoformat() if response.created_at else None,
                'updated_at': response.updated_at.isoformat() if response.updated_at else None,
                # Blood request details
                'blood_request': {
                    'hospital_name': req.hospital.hospital_name if req.hospital else None,
                    'blood_group_name': req.blood_group.blood_group_name if req.blood_group else None,
                    'no_of_units': req.no_of_units,
                    'patient_name': req.patient_name,
                    'required_by_date': req.required_by_date.isoformat() if req.required_by_date else None,
                    'status': req.status,
                    'description': req.description
                }
            })
        return jsonify({'total_donations': len(result), 'donations': result}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get scheduled donations: {str(e)}'}), 500

@blood_bp.route('/donations', methods=['GET'])
def get_all_donations():
    """Get all scheduled donations (for admin or general view)."""
    try:
        # Try to get current user ID, but don't require authentication
        current_user_id = None
        try:
            current_user_id = get_jwt_identity()
        except:
            # If no valid token, continue without user filtering
            pass
        
        # Get query parameters for filtering
        status = request.args.get('status')
        blood_group_id = request.args.get('blood_group_id')
        hospital_id = request.args.get('hospital_id')
        user_id = request.args.get('user_id')
        
        # Build query for responses with scheduled datetime
        query = BloodRequestResponse.query.filter(
            BloodRequestResponse.scheduled_datetime != None
        )
        
        # Apply filters
        if status:
            query = query.filter(BloodRequestResponse.response_status == status)
        if user_id:
            query = query.filter(BloodRequestResponse.user_id == user_id)
        
        # Join with related tables using explicit join conditions
        responses = query.join(
            BloodRequest, 
            BloodRequestResponse.blood_request_id == BloodRequest.blood_request_id
        ).join(
            Hospital, 
            BloodRequest.hospital_id == Hospital.hospital_id
        ).join(
            LookupBloodGroup, 
            BloodRequest.blood_group_type == LookupBloodGroup.blood_group_id
        ).join(
            User, 
            BloodRequestResponse.user_id == User.user_id
        ).all()
        
        result = []
        for response in responses:
            req = response.blood_request
            result.append({
                'blood_requests_response_id': response.blood_requests_response_id,
                'blood_request_id': response.blood_request_id,
                'scheduled_datetime': response.scheduled_datetime.isoformat() if response.scheduled_datetime else None,
                'response_status': response.response_status,
                'message': response.message,
                'from_date': response.from_date.isoformat() if response.from_date else None,
                'to_date': response.to_date.isoformat() if response.to_date else None,
                'created_at': response.created_at.isoformat() if response.created_at else None,
                'updated_at': response.updated_at.isoformat() if response.updated_at else None,
                # Blood request details
                'patient_name': req.patient_name,
                'no_of_units': req.no_of_units,
                'required_by_date': req.required_by_date.isoformat() if req.required_by_date else None,
                'description': req.description,
                'blood_request_status': req.status,
                # Hospital details
                'hospital_id': req.hospital_id,
                'hospital_name': req.hospital.hospital_name,
                # Blood group details
                'blood_group_type': req.blood_group_type,
                'blood_group_name': req.blood_group.blood_group_name,
                # Donor details
                'donor_id': response.user_id,
                'donor_name': response.user.user_name,
                'donor_email': response.user.emailaddress,
                'donor_phone': response.user.phonenumber
            })
        
        # Return just the array directly to match frontend expectations
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get donations: {str(e)}'}), 500

def send_email_notification(to_email, subject, body):
    # Placeholder for sending email
    current_app.logger.info(f"Sending email to {to_email}: {subject}\n{body}")
    # Implement actual email logic here
    pass

# POST /blood-response: Create a blood donation response
@blood_bp.route('/blood-response', methods=['POST'])
@jwt_required()
def create_blood_response():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['blood_request_id', 'response_status', 'from_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate response_status
        valid_statuses = ['Pending', 'Accepted', 'Rejected']
        if data['response_status'] not in valid_statuses:
            return jsonify({'error': f"response_status must be one of {valid_statuses}"}), 400

        # Get user_id from JWT if not provided
        user_id = data.get('user_id')
        if not user_id:
            user_id = get_jwt_identity()
        else:
            # Optionally, ensure user_id matches JWT for security
            jwt_user_id = get_jwt_identity()
            if int(user_id) != int(jwt_user_id):
                return jsonify({'error': 'user_id does not match authenticated user'}), 403

        blood_request_id = data['blood_request_id']
        # Prevent duplicate responses
        existing = BloodRequestResponse.query.filter_by(blood_request_id=blood_request_id, user_id=user_id).first()
        if existing:
            return jsonify({'error': 'You have already responded to this request'}), 400

        # Validate blood_request exists
        blood_request = BloodRequest.query.get(blood_request_id)
        if not blood_request:
            return jsonify({'error': 'Blood request not found'}), 404

        # Prepare fields
        message = data.get('message')
        from_date = data['from_date']
        scheduled_datetime = data.get('scheduled_datetime')
        now = datetime.now()
        response = BloodRequestResponse(
            blood_request_id=blood_request_id,
            user_id=user_id,
            response_status=data['response_status'],
            message=message,
            from_date=from_date,
            responded_date=now,
            scheduled_datetime=scheduled_datetime,
            created_at=now,
            updated_at=now
        )
        db.session.add(response)
        db.session.commit()

        # Bonus: Send email if accepted
        if data['response_status'] == 'Accepted':
            # Email hospital or user (placeholder logic)
            hospital_email = getattr(blood_request.hospital, 'hospital_email_id', None)
            if hospital_email:
                send_email_notification(hospital_email, 'Blood Donation Accepted', f"A donor has accepted your blood request (ID: {blood_request_id}).")

        return jsonify({
            'message': 'Blood response created successfully',
            'blood_requests_response_id': response.blood_requests_response_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create blood response: {str(e)}'}), 500

# GET /blood-response: Get responses by user (JWT or user_id param)
@blood_bp.route('/blood-response', methods=['GET'])
@jwt_required()
def get_blood_responses():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            user_id = get_jwt_identity()
        responses = BloodRequestResponse.query.filter_by(user_id=user_id).all()
        result = []
        for response in responses:
            result.append({
                'blood_requests_response_id': response.blood_requests_response_id,
                'blood_request_id': response.blood_request_id,
                'response_status': response.response_status,
                'message': response.message,
                'from_date': response.from_date.isoformat() if response.from_date else None,
                'responded_date': response.responded_date.isoformat() if response.responded_date else None,
                'scheduled_datetime': response.scheduled_datetime.isoformat() if response.scheduled_datetime else None,
                'created_at': response.created_at.isoformat() if response.created_at else None,
                'updated_at': response.updated_at.isoformat() if response.updated_at else None
            })
        return jsonify({'responses': result, 'total': len(result)}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get responses: {str(e)}'}), 500

@blood_bp.route('/requests/my', methods=['GET'])
@jwt_required()
def get_hospital_blood_requests():
    try:
        current_user_id = get_jwt_identity()
        
        # Find the hospital for this admin through UserHospitalAdminLineage
        admin_lineage = UserHospitalAdminLineage.query.filter_by(user_id=current_user_id).first()
        
        if not admin_lineage:
            return jsonify({'error': 'Hospital not found for current user'}), 404

        requests = BloodRequest.query.filter_by(hospital_id=admin_lineage.hospital_id).all()
        result = [{
            "blood_request_id": req.blood_request_id,
            "patient_name": req.patient_name,
            "blood_group_type": req.blood_group.blood_group_name if req.blood_group else req.blood_group_type,
            "no_of_units": req.no_of_units,
            "status": req.status
        } for req in requests]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get hospital blood requests: {str(e)}'}), 500