from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from ..models.models import Patient, Doctor, Admin

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "admin":
                return jsonify({"msg": "Admin access required"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def doctor_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "doctor":
                return jsonify({"msg": "Doctor access required"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def patient_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "patient":
                return jsonify({"msg": "Patient access required"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def get_current_user():
    claims = get_jwt()
    user_id = get_jwt_identity()
    role = claims.get("role")
    
    if role == "patient":
        return Patient.query.get(user_id)
    elif role == "doctor":
        return Doctor.query.get(user_id)
    elif role == "admin":
        return Admin.query.get(user_id)
    return None

def generate_token_response(user, role):
    from flask_jwt_extended import create_access_token, create_refresh_token
    
    access_token = create_access_token(
        identity=user.patient_id if role == "patient" else user.doctor_id if role == "doctor" else user.admin_id,
        additional_claims={"role": role}
    )
    refresh_token = create_refresh_token(
        identity=user.patient_id if role == "patient" else user.doctor_id if role == "doctor" else user.admin_id,
        additional_claims={"role": role}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "role": role
    } 