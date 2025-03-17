from app import create_app, db
from app.models.models import Patient, Doctor, Admin, Appointment, MedicalReport, Prescription, Payment, Feedback

def init_db():
    app = create_app('development')
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 