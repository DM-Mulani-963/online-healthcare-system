from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from ..models.models import db, Patient, Doctor, Admin
from ..utils.auth import generate_token_response
from flasgger import swag_from

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register/patient', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Register a new patient',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'first_name': {'type': 'string'},
                    'last_name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'password': {'type': 'string'},
                    'date_of_birth': {'type': 'string', 'format': 'date'},
                    'contact_number': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Patient registered successfully'
        },
        '400': {
            'description': 'Invalid input data'
        }
    }
})
def register_patient():
    data = request.get_json()
    
    # Check if email already exists
    if Patient.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400
        
    try:
        patient = Patient(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            username=data['email'],  # Using email as username
            date_of_birth=data['date_of_birth'],
            contact_number=data['contact_number']
        )
        patient.set_password(data['password'])
        
        db.session.add(patient)
        db.session.commit()
        
        return jsonify({
            'message': 'Patient registered successfully',
            **generate_token_response(patient, 'patient')
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400

@auth_bp.route('/register/doctor', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Register a new doctor',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'first_name': {'type': 'string'},
                    'last_name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'password': {'type': 'string'},
                    'specialization': {'type': 'string'},
                    'contact_number': {'type': 'string'},
                    'consultation_fees': {'type': 'number'}
                }
            }
        }
    ]
})
def register_doctor():
    data = request.get_json()
    
    if Doctor.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400
        
    try:
        doctor = Doctor(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            username=data['email'],
            specialization=data['specialization'],
            contact_number=data['contact_number'],
            consultation_fees=data['consultation_fees']
        )
        doctor.set_password(data['password'])
        
        db.session.add(doctor)
        db.session.commit()
        
        return jsonify({
            'message': 'Doctor registered successfully',
            **generate_token_response(doctor, 'doctor')
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Login for patients, doctors, and admins',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string'},
                    'password': {'type': 'string'},
                    'role': {'type': 'string', 'enum': ['patient', 'doctor', 'admin']}
                }
            }
        }
    ]
})
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'patient')
    
    if role == 'patient':
        user = Patient.query.filter_by(email=email).first()
    elif role == 'doctor':
        user = Doctor.query.filter_by(email=email).first()
    elif role == 'admin':
        user = Admin.query.filter_by(email=email).first()
    else:
        return jsonify({'message': 'Invalid role'}), 400
        
    if user and user.check_password(password):
        return jsonify(generate_token_response(user, role)), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token), 200 