from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.blood_request import BloodRequest
from models.hospital import Hospital
from models.user import User
from schemas.blood_request_schema import BloodRequestSchema
from db import db

blood_requests_bp = Blueprint('blood_requests', __name__)
schema = BloodRequestSchema()

@blood_requests_bp.route('/blood/request', methods=['POST'])
@jwt_required()
def create_blood_request():
    data = request.get_json()
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    user_id = get_jwt_identity()
    blood_request = BloodRequest(
        patient_name=data['patient_name'],
        patient_contact=data['patient_contact'],
        blood_group_id=data['blood_group_id'],
        hospital_id=data['hospital_id'],
        status='pending',
        created_by=user_id
    )
    db.session.add(blood_request)
    db.session.commit()
    return schema.jsonify(blood_request), 201

@blood_requests_bp.route('/blood/requests', methods=['GET'])
@jwt_required()
def list_blood_requests():
    requests = BloodRequest.query.all()
    return schema.jsonify(requests, many=True), 200

@blood_requests_bp.route('/blood/request/<int:request_id>', methods=['GET'])
@jwt_required()
def get_blood_request(request_id):
    req = BloodRequest.query.get_or_404(request_id)
    return schema.jsonify(req), 200

@blood_requests_bp.route('/blood/request/<int:request_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def edit_blood_request(request_id):
    req = BloodRequest.query.get_or_404(request_id)
    data = request.get_json()
    errors = schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400
    for key, value in data.items():
        setattr(req, key, value)
    db.session.commit()
    return schema.jsonify(req), 200

@blood_requests_bp.route('/blood/request/<int:request_id>', methods=['DELETE'])
@jwt_required()
def delete_blood_request(request_id):
    req = BloodRequest.query.get_or_404(request_id)
    db.session.delete(req)
    db.session.commit()
    return '', 204

@blood_requests_bp.route('/blood/request/<int:request_id>/respond', methods=['POST'])
@jwt_required()
def respond_blood_request(request_id):
    # Example: Accept or reject a request
    req = BloodRequest.query.get_or_404(request_id)
    data = request.get_json()
    status = data.get('status')
    if status not in ['accepted', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400
    req.status = status
    db.session.commit()
    return schema.jsonify(req), 200

@blood_requests_bp.route('/blood/request/<int:request_id>/export', methods=['GET'])
@jwt_required()
def export_blood_request(request_id):
    # Placeholder: implement export logic (e.g., PDF/CSV)
    return jsonify({'message': 'Export not implemented'}), 501

@blood_requests_bp.route('/blood/request/<int:request_id>/share', methods=['POST'])
@jwt_required()
def share_blood_request(request_id):
    # Placeholder: implement share logic (e.g., send email)
    return jsonify({'message': 'Share not implemented'}), 501

@blood_requests_bp.route('/blood/request/<int:request_id>/message', methods=['POST'])
@jwt_required()
def message_blood_request(request_id):
    # Placeholder: implement message logic
    return jsonify({'message': 'Message not implemented'}), 501 