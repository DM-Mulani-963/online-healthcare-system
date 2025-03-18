const express = require('express');
const cors = require('cors');
const db = require('./config/db');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Test DB Connection
app.get('/api/test', async (req, res) => {
    try {
        const [rows] = await db.query('SELECT 1');
        res.json({ message: 'Database connection successful', data: rows });
    } catch (error) {
        res.status(500).json({ message: 'Database connection failed', error: error.message });
    }
});

// Patient Routes
app.post('/api/patients/register', async (req, res) => {
    try {
        const { firstName, lastName, email, password, contact, address, dateOfBirth, gender } = req.body;
        const [result] = await db.query(
            'INSERT INTO patient (First_Name, Last_Name, Email, Password, Contact, Address, Date_of_Birth, Gender) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            [firstName, lastName, email, password, contact, address, dateOfBirth, gender]
        );
        res.json({ message: 'Patient registered successfully', patientId: result.insertId });
    } catch (error) {
        res.status(500).json({ message: 'Registration failed', error: error.message });
    }
});

app.post('/api/patients/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        const [patients] = await db.query(
            'SELECT * FROM patient WHERE Email = ? AND Password = ?',
            [email, password]
        );
        if (patients.length > 0) {
            res.json({ message: 'Login successful', patient: patients[0] });
        } else {
            res.status(401).json({ message: 'Invalid credentials' });
        }
    } catch (error) {
        res.status(500).json({ message: 'Login failed', error: error.message });
    }
});

// Doctor Routes
app.get('/api/doctors', async (req, res) => {
    try {
        const [doctors] = await db.query('SELECT * FROM doctor');
        res.json(doctors);
    } catch (error) {
        res.status(500).json({ message: 'Failed to fetch doctors', error: error.message });
    }
});

app.get('/api/doctors/:specialization', async (req, res) => {
    try {
        const [doctors] = await db.query(
            'SELECT * FROM doctor WHERE Specialization = ?',
            [req.params.specialization]
        );
        res.json(doctors);
    } catch (error) {
        res.status(500).json({ message: 'Failed to fetch doctors', error: error.message });
    }
});

// Appointment Routes
app.post('/api/appointments', async (req, res) => {
    try {
        const { patientId, doctorId, date, time, mode } = req.body;
        const [result] = await db.query(
            'INSERT INTO appointment (Patient_ID, Doctor_ID, Date, Time, Status, Mode, Payment_Status) VALUES (?, ?, ?, ?, "Pending", ?, "Pending")',
            [patientId, doctorId, date, time, mode]
        );
        res.json({ message: 'Appointment booked successfully', appointmentId: result.insertId });
    } catch (error) {
        res.status(500).json({ message: 'Booking failed', error: error.message });
    }
});

app.get('/api/appointments/patient/:patientId', async (req, res) => {
    try {
        const [appointments] = await db.query(
            `SELECT a.*, 
                    d.First_Name as doctor_first_name, 
                    d.Last_Name as doctor_last_name, 
                    d.Specialization 
             FROM appointment a 
             JOIN doctor d ON a.Doctor_ID = d.Doctor_ID 
             WHERE a.Patient_ID = ?`,
            [req.params.patientId]
        );
        res.json(appointments);
    } catch (error) {
        res.status(500).json({ message: 'Failed to fetch appointments', error: error.message });
    }
});

// Medical Report Routes
app.post('/api/medical-reports', async (req, res) => {
    try {
        const { patientId, doctorId, diagnosis, prescription, notes, date } = req.body;
        const [result] = await db.query(
            'INSERT INTO medical_report (Patient_ID, Doctor_ID, Diagnosis, Prescription, Notes, Date) VALUES (?, ?, ?, ?, ?, ?)',
            [patientId, doctorId, diagnosis, prescription, notes, date]
        );
        res.json({ message: 'Medical report created successfully', reportId: result.insertId });
    } catch (error) {
        res.status(500).json({ message: 'Failed to create medical report', error: error.message });
    }
});

app.get('/api/medical-reports/patient/:patientId', async (req, res) => {
    try {
        const [reports] = await db.query(
            `SELECT mr.*, 
                    d.First_Name as doctor_first_name, 
                    d.Last_Name as doctor_last_name 
             FROM medical_report mr 
             JOIN doctor d ON mr.Doctor_ID = d.Doctor_ID 
             WHERE mr.Patient_ID = ?`,
            [req.params.patientId]
        );
        res.json(reports);
    } catch (error) {
        res.status(500).json({ message: 'Failed to fetch medical reports', error: error.message });
    }
});

// Payment Routes
app.post('/api/payments', async (req, res) => {
    try {
        const { appointmentId, amount, paymentMethod } = req.body;
        const [result] = await db.query(
            'INSERT INTO payment (Appointment_ID, Amount, Payment_Method, Status, Date) VALUES (?, ?, ?, "Completed", CURRENT_DATE)',
            [appointmentId, amount, paymentMethod]
        );
        
        // Update appointment payment status
        await db.query(
            'UPDATE appointment SET Payment_Status = "Paid" WHERE Appointment_ID = ?',
            [appointmentId]
        );
        
        res.json({ message: 'Payment processed successfully', paymentId: result.insertId });
    } catch (error) {
        res.status(500).json({ message: 'Payment processing failed', error: error.message });
    }
});

// Feedback Routes
app.post('/api/feedback', async (req, res) => {
    try {
        const { patientId, doctorId, rating, comment } = req.body;
        const [result] = await db.query(
            'INSERT INTO feedback (Patient_ID, Doctor_ID, Rating, Comment, Date) VALUES (?, ?, ?, ?, CURRENT_DATE)',
            [patientId, doctorId, rating, comment]
        );
        res.json({ message: 'Feedback submitted successfully', feedbackId: result.insertId });
    } catch (error) {
        res.status(500).json({ message: 'Failed to submit feedback', error: error.message });
    }
});

const PORT = process.env.PORT || 5500;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
}); 