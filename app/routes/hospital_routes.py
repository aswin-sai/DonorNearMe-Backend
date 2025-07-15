from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Hospital, HospitalBloodAvailability, LookupBloodGroup, UserHospitalAdminLineage, BloodRequest
from app.schemas.hospital_schemas import HospitalSchema
from marshmallow import ValidationError
from datetime import datetime, date

hospital_bp = Blueprint('hospital', __name__)

# Initialize schema
hospital_schema = HospitalSchema()

@hospital_bp.route('/register', methods=['POST'])
@jwt_required()
def register_hospital():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate input data
        try:
            validated_data = hospital_schema.load(data)
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Check if hospital with same email already exists
        if validated_data.get('hospital_email_id'):
            existing_hospital = Hospital.query.filter_by(
                hospital_email_id=validated_data['hospital_email_id']
            ).first()
            if existing_hospital:
                return jsonify({'error': 'Hospital with this email already exists'}), 409
        
        # Create new hospital
        new_hospital = Hospital(
            hospital_name=validated_data['hospital_name'],
            from_date=date.today(),
            hospital_address=validated_data.get('hospital_address'),
            hospital_contact_number=validated_data.get('hospital_contact_number'),
            hospital_email_id=validated_data.get('hospital_email_id'),
            hospital_contact_person=validated_data.get('hospital_contact_person'),
            hospital_pincode=validated_data.get('hospital_pincode'),
            hospital_type=validated_data.get('hospital_type'),
            has_blood_bank=validated_data.get('has_blood_bank', False)
        )
        
        db.session.add(new_hospital)
        db.session.commit()
        
        return jsonify({
            'message': 'Hospital registered successfully',
            'hospital_id': new_hospital.hospital_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@hospital_bp.route('/list', methods=['GET'])
def list_hospitals():
    try:
        hospitals = Hospital.query.all()
        result = []
        for hospital in hospitals:
            result.append({
                'hospital_id': hospital.hospital_id,
                'hospital_name': hospital.hospital_name,
                'hospital_address': hospital.hospital_address,
                'hospital_contact_number': hospital.hospital_contact_number,
                'hospital_email_id': hospital.hospital_email_id,
                'hospital_contact_person': hospital.hospital_contact_person,
                'hospital_pincode': hospital.hospital_pincode,
                'hospital_type': hospital.hospital_type,
                'has_blood_bank': hospital.has_blood_bank,
                'from_date': hospital.from_date.isoformat() if hospital.from_date else None,
                'to_date': hospital.to_date.isoformat() if hospital.to_date else None
            })
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@hospital_bp.route('/<int:hospital_id>', methods=['GET'])
def get_hospital(hospital_id):
    try:
        hospital = Hospital.query.get(hospital_id)
        if not hospital:
            return jsonify({'error': 'Hospital not found'}), 404
        
        result = {
            'hospital_id': hospital.hospital_id,
            'hospital_name': hospital.hospital_name,
            'hospital_address': hospital.hospital_address,
            'hospital_contact_number': hospital.hospital_contact_number,
            'hospital_email_id': hospital.hospital_email_id,
            'hospital_contact_person': hospital.hospital_contact_person,
            'hospital_pincode': hospital.hospital_pincode,
            'hospital_type': hospital.hospital_type,
            'has_blood_bank': hospital.has_blood_bank,
            'from_date': hospital.from_date.isoformat() if hospital.from_date else None,
            'to_date': hospital.to_date.isoformat() if hospital.to_date else None
        }
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@hospital_bp.route('/update_blood_availability', methods=['POST'])
@jwt_required()
def update_blood_availability():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['hospital_id', 'blood_group_id', 'no_of_units']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate hospital exists
        hospital = Hospital.query.get(data['hospital_id'])
        if not hospital:
            return jsonify({'error': 'Hospital not found'}), 404
        
        # Validate blood group exists
        blood_group = LookupBloodGroup.query.get(data['blood_group_id'])
        if not blood_group:
            return jsonify({'error': 'Blood group not found'}), 404
        
        # Check if availability record exists
        availability = HospitalBloodAvailability.query.filter_by(
            hospital_id=data['hospital_id'],
            blood_group_id=data['blood_group_id']
        ).first()
        
        if availability:
            # Update existing record
            availability.no_of_units = data['no_of_units']
            availability.to_date = None  # Reset to_date if updating
        else:
            # Create new record
            availability = HospitalBloodAvailability(
                hospital_id=data['hospital_id'],
                blood_group_id=data['blood_group_id'],
                no_of_units=data['no_of_units'],
                from_date=date.today()
            )
            db.session.add(availability)
        
        db.session.commit()
        return jsonify({'message': 'Blood availability updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@hospital_bp.route('/availability', methods=['GET'])
def get_availability():
    try:
        hospital_id = request.args.get('hospital_id')
        
        if not hospital_id:
            return jsonify({'error': 'Missing hospital_id parameter'}), 400
        
        # Validate hospital exists
        hospital = Hospital.query.get(hospital_id)
        if not hospital:
            return jsonify({'error': 'Hospital not found'}), 404
        
        availabilities = HospitalBloodAvailability.query.filter_by(
            hospital_id=hospital_id
        ).join(LookupBloodGroup).all()
        
        result = []
        for availability in availabilities:
            result.append({
                'blood_group_id': availability.blood_group_id,
                'blood_group_name': availability.blood_group.blood_group_name,
                'no_of_units': availability.no_of_units,
                'from_date': availability.from_date.isoformat() if availability.from_date else None,
                'to_date': availability.to_date.isoformat() if availability.to_date else None
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@hospital_bp.route('/search', methods=['GET'])
def search_hospitals():
    try:
        # Get search parameters
        name = request.args.get('name')
        pincode = request.args.get('pincode')
        has_blood_bank = request.args.get('has_blood_bank')
        
        # Build query
        query = Hospital.query
        
        if name:
            query = query.filter(Hospital.hospital_name.ilike(f'%{name}%'))
        if pincode:
            query = query.filter(Hospital.hospital_pincode == pincode)
        if has_blood_bank:
            has_blood_bank_bool = has_blood_bank.lower() == 'true'
            query = query.filter(Hospital.has_blood_bank == has_blood_bank_bool)
        
        hospitals = query.all()
        
        result = []
        for hospital in hospitals:
            result.append({
                'hospital_id': hospital.hospital_id,
                'hospital_name': hospital.hospital_name,
                'hospital_address': hospital.hospital_address,
                'hospital_contact_number': hospital.hospital_contact_number,
                'hospital_email_id': hospital.hospital_email_id,
                'hospital_contact_person': hospital.hospital_contact_person,
                'hospital_pincode': hospital.hospital_pincode,
                'hospital_type': hospital.hospital_type,
                'has_blood_bank': hospital.has_blood_bank
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@hospital_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_hospital_stats():
    try:
        current_user_id = get_jwt_identity()
        
        # Find the hospital for this admin through UserHospitalAdminLineage
        admin_lineage = UserHospitalAdminLineage.query.filter_by(user_id=current_user_id).first()
        
        if not admin_lineage:
            return jsonify({'error': 'Hospital not found for current user'}), 404

        # Dummy values for unitsAvailable and critical (replace with real queries if available)
        units_available = 120
        critical = 2
        # Count active and fulfilled requests for this hospital
        active_requests = BloodRequest.query.filter_by(hospital_id=admin_lineage.hospital_id, status='pending').count()
        fulfilled = BloodRequest.query.filter_by(hospital_id=admin_lineage.hospital_id, status='completed').count()

        return jsonify({
            "unitsAvailable": units_available,
            "activeRequests": active_requests,
            "fulfilled": fulfilled,
            "critical": critical
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get hospital stats: {str(e)}'}), 500