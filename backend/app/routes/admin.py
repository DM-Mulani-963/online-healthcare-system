from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models.models import db, Admin, Doctor, Patient, Appointment, MedicalReport, Prescription, Feedback
from ..utils.auth import admin_required
from flasgger import swag_from
from sqlalchemy import func
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/doctors', methods=['GET'])
@jwt_required()
@admin_required
@swag_from({
    'tags': ['Admin'],
    'description': 'Get all doctors with optional filters',
    'parameters': [
        {
            'name': 'specialization',
            'in': 'query',
            'type': 'string',
            'required': False
        },
        {
            'name': 'status',
            'in': 'query',
            'type': 'string',
            'required': False
        }
    ]
})
def get_doctors():
    specialization = request.args.get('specialization')
    status = request.args.get('status')
    
    query = Doctor.query
    if specialization:
        query = query.filter_by(specialization=specialization)
    if status:
        query = query.filter_by(status=status)
        
    doctors = query.all()
    
    return jsonify([{
        'id': doc.id,
        'first_name': doc.first_name,
        'last_name': doc.last_name,
        'email': doc.email,
        'specialization': doc.specialization,
        'contact_number': doc.contact_number,
        'consultation_fees': doc.consultation_fees,
        'status': doc.status
    } for doc in doctors]), 200

@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@jwt_required()
@admin_required
@swag_from({
    'tags': ['Admin'],
    'description': 'Update doctor status',
    'parameters': [
        {
            'name': 'doctor_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'enum': ['active', 'inactive', 'suspended']}
                }
            }
        }
    ]
})
def update_doctor_status(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    data = request.get_json()
    
    try:
        doctor.status = data['status']
        db.session.commit()
        return jsonify({'message': 'Doctor status updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400

@admin_bp.route('/patients', methods=['GET'])
@jwt_required()
@admin_required
def get_patients():
    patients = Patient.query.all()
    
    return jsonify([{
        'id': patient.id,
        'first_name': patient.first_name,
        'last_name': patient.last_name,
        'email': patient.email,
        'contact_number': patient.contact_number,
        'date_of_birth': patient.date_of_birth.isoformat()
    } for patient in patients]), 200

@admin_bp.route('/appointments', methods=['GET'])
@jwt_required()
@admin_required
@swag_from({
    'tags': ['Admin'],
    'description': 'Get all appointments with optional filters',
    'parameters': [
        {
            'name': 'status',
            'in': 'query',
            'type': 'string',
            'required': False
        },
        {
            'name': 'date',
            'in': 'query',
            'type': 'string',
            'format': 'date',
            'required': False
        }
    ]
})
def get_appointments():
    status = request.args.get('status')
    date_str = request.args.get('date')
    
    query = Appointment.query
    if status:
        query = query.filter_by(status=status)
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        query = query.filter(Appointment.appointment_date == date)
        
    appointments = query.all()
    
    return jsonify([{
        'id': apt.id,
        'patient_name': f"{apt.patient.first_name} {apt.patient.last_name}",
        'doctor_name': f"{apt.doctor.first_name} {apt.doctor.last_name}",
        'date': apt.appointment_date.isoformat(),
        'time': apt.appointment_time.strftime('%H:%M'),
        'status': apt.status,
        'mode': apt.mode,
        'payment_status': apt.payment_status
    } for apt in appointments]), 200

@admin_bp.route('/statistics', methods=['GET'])
@jwt_required()
@admin_required
def get_statistics():
    # Get date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Total counts
    total_patients = Patient.query.count()
    total_doctors = Doctor.query.count()
    total_appointments = Appointment.query.count()
    
    # Monthly statistics
    monthly_appointments = Appointment.query.filter(
        Appointment.appointment_date.between(start_date, end_date)
    ).count()
    
    monthly_revenue = db.session.query(
        func.sum(Doctor.consultation_fees)
    ).join(Appointment).filter(
        Appointment.appointment_date.between(start_date, end_date),
        Appointment.status == 'completed',
        Appointment.payment_status == 'paid'
    ).scalar() or 0
    
    # Appointment statistics
    appointment_status = db.session.query(
        Appointment.status,
        func.count(Appointment.id)
    ).group_by(Appointment.status).all()
    
    # Doctor statistics
    doctor_specializations = db.session.query(
        Doctor.specialization,
        func.count(Doctor.id)
    ).group_by(Doctor.specialization).all()
    
    return jsonify({
        'total_statistics': {
            'patients': total_patients,
            'doctors': total_doctors,
            'appointments': total_appointments
        },
        'monthly_statistics': {
            'appointments': monthly_appointments,
            'revenue': float(monthly_revenue)
        },
        'appointment_status': dict(appointment_status),
        'doctor_specializations': dict(doctor_specializations)
    }), 200

@admin_bp.route('/feedback', methods=['GET'])
@jwt_required()
@admin_required
def get_feedback():
    feedback = db.session.query(
        Feedback,
        Patient.first_name.label('patient_first_name'),
        Patient.last_name.label('patient_last_name'),
        Doctor.first_name.label('doctor_first_name'),
        Doctor.last_name.label('doctor_last_name')
    ).join(Patient).join(Doctor).all()
    
    return jsonify([{
        'id': f.Feedback.id,
        'patient_name': f'{f.patient_first_name} {f.patient_last_name}',
        'doctor_name': f'{f.doctor_first_name} {f.doctor_last_name}',
        'rating': f.Feedback.rating,
        'comment': f.Feedback.comment,
        'date': f.Feedback.date.isoformat()
    } for f in feedback]), 200

@admin_bp.route('/reports', methods=['GET'])
@jwt_required()
@admin_required
@swag_from({
    'tags': ['Admin'],
    'description': 'Generate various administrative reports',
    'parameters': [
        {
            'name': 'report_type',
            'in': 'query',
            'type': 'string',
            'required': True,
            'enum': ['revenue', 'appointments', 'doctors', 'patients']
        },
        {
            'name': 'start_date',
            'in': 'query',
            'type': 'string',
            'format': 'date',
            'required': False
        },
        {
            'name': 'end_date',
            'in': 'query',
            'type': 'string',
            'format': 'date',
            'required': False
        }
    ]
})
def generate_report():
    report_type = request.args.get('report_type')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    
    if report_type == 'revenue':
        query = db.session.query(
            Appointment.appointment_date,
            func.sum(Doctor.consultation_fees)
        ).join(Doctor).filter(
            Appointment.status == 'completed',
            Appointment.payment_status == 'paid'
        )
        
        if start_date:
            query = query.filter(Appointment.appointment_date >= start_date)
        if end_date:
            query = query.filter(Appointment.appointment_date <= end_date)
            
        results = query.group_by(Appointment.appointment_date).all()
        
        return jsonify([{
            'date': date.isoformat(),
            'revenue': float(revenue)
        } for date, revenue in results]), 200
        
    elif report_type == 'appointments':
        query = db.session.query(
            Appointment.appointment_date,
            func.count(Appointment.id)
        )
        
        if start_date:
            query = query.filter(Appointment.appointment_date >= start_date)
        if end_date:
            query = query.filter(Appointment.appointment_date <= end_date)
            
        results = query.group_by(Appointment.appointment_date).all()
        
        return jsonify([{
            'date': date.isoformat(),
            'count': count
        } for date, count in results]), 200
        
    elif report_type == 'doctors':
        doctors = Doctor.query.all()
        
        return jsonify([{
            'id': doc.id,
            'name': f"{doc.first_name} {doc.last_name}",
            'specialization': doc.specialization,
            'appointment_count': len(doc.appointments),
            'average_rating': sum(f.rating for f in doc.feedback) / len(doc.feedback) if doc.feedback else 0
        } for doc in doctors]), 200
        
    elif report_type == 'patients':
        patients = Patient.query.all()
        
        return jsonify([{
            'id': pat.id,
            'name': f"{pat.first_name} {pat.last_name}",
            'appointment_count': len(pat.appointments),
            'last_visit': max(apt.appointment_date for apt in pat.appointments).isoformat() if pat.appointments else None
        } for pat in patients]), 200
        
    return jsonify({'message': 'Invalid report type'}), 400 