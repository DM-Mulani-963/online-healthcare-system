from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from celery import Celery
from flasgger import Swagger
from dotenv import load_dotenv
import os

from config.config import config

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)
celery = Celery()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    limiter.init_app(app)
    
    # Configure Celery
    celery.conf.update(app.config)
    
    # Configure Swagger
    Swagger(app)
    
    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.patient import patient_bp
    from .routes.doctor import doctor_bp
    from .routes.admin import admin_bp
    from .routes.appointment import appointment_bp
    from .routes.medical_report import medical_report_bp
    from .routes.prescription import prescription_bp
    from .routes.payment import payment_bp
    from .routes.feedback import feedback_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(patient_bp, url_prefix='/api/patients')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctors')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(appointment_bp, url_prefix='/api/appointments')
    app.register_blueprint(medical_report_bp, url_prefix='/api/medical-reports')
    app.register_blueprint(prescription_bp, url_prefix='/api/prescriptions')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200
    
    return app 