from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.models import db, Patient, Appointment, MedicalReport, Prescription, Doctor, Feedback
from ..utils.auth import patient_required
from flasgger import swag_from
from datetime import datetime

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/profile', methods=['GET'])
@jwt_required()
@patient_required
@swag_from({
    'tags': ['Patient'],
    'description': 'Get patient profile information',
    'responses': {
        '200': {
            'description': 'Patient profile retrieved successfully'
        }
    }
})
def get_profile():
    patient_id = get_jwt_identity()
    patient = Patient.query.get_or_404(patient_id)
    
    return jsonify({
        'id': patient.id,
        'first_name': patient.first_name,
        'last_name': patient.last_name,
        'email': patient.email,
        'date_of_birth': patient.date_of_birth.isoformat(),
        'contact_number': patient.contact_number
    }), 200

@patient_bp.route('/profile', methods=['PUT'])
@jwt_required()
@patient_required
@swag_from({
    'tags': ['Patient'],
    'description': 'Update patient profile information',
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
                    'contact_number': {'type': 'string'},
                    'date_of_birth': {'type': 'string', 'format': 'date'}
                }
            }
        }
    ]
})
def update_profile():
    patient_id = get_jwt_identity()
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json()
    
    try:
        if 'first_name' in data:
            patient.first_name = data['first_name']
        if 'last_name' in data:
            patient.last_name = data['last_name']
        if 'contact_number' in data:
            patient.contact_number = data['contact_number']
        if 'date_of_birth' in data:
            patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400

@patient_bp.route('/appointments', methods=['GET'])
@jwt_required()
@patient_required
@swag_from({
    'tags': ['Patient'],
    'description': 'Get patient appointments',
    'parameters': [
        {
            'name': 'status',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter by appointment status'
        }
    ]
})
def get_appointments():
    patient_id = get_jwt_identity()
    status = request.args.get('status')
    
    query = Appointment.query.filter_by(patient_id=patient_id)
    if status:
        query = query.filter_by(status=status)
        
    appointments = query.all()
    
    return jsonify([{
        'id': apt.id,
        'doctor_name': f"{apt.doctor.first_name} {apt.doctor.last_name}",
        'date': apt.appointment_date.isoformat(),
        'time': apt.appointment_time.strftime('%H:%M'),
        'status': apt.status,
        'mode': apt.mode,
        'payment_status': apt.payment_status
    } for apt in appointments]), 200

@patient_bp.route('/medical-reports', methods=['GET'])
@jwt_required()
@patient_required
def get_medical_reports():
    patient_id = get_jwt_identity()
    reports = MedicalReport.query.filter_by(patient_id=patient_id).all()
    
    return jsonify([{
        'id': report.id,
        'doctor_name': f"{report.doctor.first_name} {report.doctor.last_name}",
        'date': report.date.isoformat(),
        'diagnosis': report.diagnosis,
        'symptoms': report.symptoms,
        'prescription_id': report.prescription_id
    } for report in reports]), 200

@patient_bp.route('/prescriptions', methods=['GET'])
@jwt_required()
@patient_required
def get_prescriptions():
    patient_id = get_jwt_identity()
    prescriptions = Prescription.query.filter_by(patient_id=patient_id).all()
    
    return jsonify([{
        'id': prescription.id,
        'doctor_name': f"{prescription.doctor.first_name} {prescription.doctor.last_name}",
        'date': prescription.date.isoformat(),
        'medications': prescription.medications,
        'dosage': prescription.dosage,
        'duration': prescription.duration
    } for prescription in prescriptions]), 200

@patient_bp.route('/doctors', methods=['GET'])
@jwt_required()
@patient_required
@swag_from({
    'tags': ['Patient'],
    'description': 'Get list of doctors',
    'parameters': [
        {
            'name': 'specialization',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter by specialization'
        }
    ]
})
def get_doctors():
    specialization = request.args.get('specialization')
    
    query = Doctor.query
    if specialization:
        query = query.filter_by(specialization=specialization)
        
    doctors = query.all()
    
    return jsonify([{
        'id': doctor.id,
        'first_name': doctor.first_name,
        'last_name': doctor.last_name,
        'specialization': doctor.specialization,
        'consultation_fees': doctor.consultation_fees
    } for doctor in doctors]), 200

@patient_bp.route('/feedback', methods=['POST'])
@jwt_required()
@patient_required
@swag_from({
    'tags': ['Patient'],
    'description': 'Submit feedback for a doctor',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'doctor_id': {'type': 'integer'},
                    'rating': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                    'comment': {'type': 'string'}
                }
            }
        }
    ]
})
def submit_feedback():
    patient_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        feedback = Feedback(
            patient_id=patient_id,
            doctor_id=data['doctor_id'],
            rating=data['rating'],
            comment=data.get('comment', '')
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({'message': 'Feedback submitted successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400 