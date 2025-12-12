import sqlite3
from utils.init_db import db_name
from models.patients import Patient
import re
from flask import flash
from datetime import datetime, date

def get_patient_by_id(id):
    """
    Fetch a patient from the database using their patient ID.
    """
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, first_name, last_name, email, date_of_birth, gender, source_row_id, created_at
    FROM patients_demographics
    WHERE id = ?
    ''', (id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Patient(*row)

    
def get_all_patients():
    """
    Fetch all patients from the database.
    """
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, first_name, last_name, email, date_of_birth, gender, source_row_id, created_at
        FROM patients_demographics
    ''')
    rows = cursor.fetchall()
    conn.close()

    patients = []
    for r in rows:
        patients.append({
            'id': r[0],
            'first_name': r[1],
            'last_name': r[2],
            'email': r[3],
            'date_of_birth': r[4],
            'gender': r[5],
            'source_row_id': r[6],
            'created_at': r[7]
        })
    return patients

def get_patients_paginated(page=1, per_page=20):
    """
    Fetch patients with pagination.
    Returns (patients_list, total_pages).
    """
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM patients_demographics")
    total_patients = cursor.fetchone()[0]

    # Calculate LIMIT / OFFSET
    offset = (page - 1) * per_page

    cursor.execute('''
        SELECT id, first_name, last_name, email, date_of_birth, gender, source_row_id, created_at
        FROM patients_demographics
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    ''', (per_page, offset))
    rows = cursor.fetchall()
    conn.close()

    patients = []
    for r in rows:
        patients.append({
            'id': r[0],
            'first_name': r[1],
            'last_name': r[2],
            'email': r[3],
            'date_of_birth': r[4],
            'gender': r[5],
            'source_row_id': r[6],
            'created_at': r[7]
        })

    # avoid division by zero
    if total_patients == 0:
        total_pages = 1
    else:
        total_pages = (total_patients + per_page - 1) // per_page

    return patients, total_pages


    
def get_patients_statistics(assessments=None):
    """
    Get statistics about patients_demographics in the system.
    """
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM patients_demographics")
    total_patients = cursor.fetchone()[0]

    conn.close()
    
    assessment_count = 0
    if assessments is not None:
        assessment_count = assessments.count_documents({})
    
    return  [
    {
        "label": "Total Patients",
        "value": total_patients,
        "description": "Registered patients in the system"
    },
    {
        "label": "Total assessments",
        "value": format(assessment_count),
        "description": "Stroke assessment made"
    }
]

def register_patient(first_name, last_name, email, date_of_birth, gender):
    """
    Register a new patient in the database.
    it returns True if successful, raises ValueError if email already exists.
    """
    # Check for empty fields
    if not first_name or not last_name or not email or not date_of_birth or not gender:
        raise ValueError('All fields are required. Please fill out all fields.')
    
    try:
        conn = sqlite3.connect(db_name())
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO patients_demographics (first_name, last_name, email, date_of_birth, gender, source_row_id)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, email, date_of_birth, gender, None))

        conn.commit()
        conn.close()
        return True
    
    except sqlite3.IntegrityError:
        raise ValueError('Patient with this email already exists in the system.')

def validate_patient_data(email=None, date_of_birth=None, gender=None):
    """
    this function validates patient data if any of the fields are passed.
    It raises ValueError with appropriate message if validation fails.
   
    """
    try:
        conn = sqlite3.connect(db_name())
        cursor = conn.cursor()
        
        
        if email:
            cursor.execute('''
            SELECT 1
            FROM patients_demographics
            WHERE email = ?
            ''', (email,))
            if cursor.fetchone(): 
                raise ValueError('Email already registered. Please use a different email')
            
            # Email pattern validation
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if not re.match(email_pattern, email):
                raise ValueError('Please enter a valid email address') 
    

        if date_of_birth:
            # Calculate age from date_of_birth
            dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 0 or age > 120:
                raise ValueError('Age must be between 0 and 120.')
        
        if gender:
            if gender not in ['male', 'female', 'other']:
                raise ValueError('Gender must be Male, Female, or Other.')
    finally:
        conn.close()
        
    
def update_patient(id, first_name, last_name, date_of_birth, gender):
    """
    Update an existing patient's information.
    """
    # Check for empty fields (using 'or' not 'and')
    if not first_name or not last_name or not date_of_birth or not gender:
        raise ValueError('All fields are required. Please fill out all fields.')
    
    try:
        conn = sqlite3.connect(db_name())
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE patients_demographics
        SET first_name = ?, last_name = ?, date_of_birth = ?, gender = ?
        WHERE id = ?
        ''', ( first_name, last_name, date_of_birth, gender, id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        raise ValueError('Failed to update patient information.')

def delete_patient(id, assessment_collection=None):
    """
    Delete a patient from the database and their assessment history from MongoDB.

    """
     # Delete patient MongoDB assessments first
    if assessment_collection is not None:
        try:
            # Delete all assessments for this patient
            assessment_collection.delete_many({"patient_id": id})

        except Exception as e:
            raise ValueError(f"Failed to delete patient assessments: {e}")
    
    # Then delete from SQLite
    try:
        conn = sqlite3.connect(db_name())
        cursor = conn.cursor()
        
        cursor.execute('''
        DELETE FROM patients_demographics
        WHERE id = ?
        ''', (id,))
        
        conn.commit()
        conn.close()
    except Exception as e:
        raise ValueError(f"Failed to delete patient: {e}")

def validate_patient_assessment_data( work_type,
    ever_married,
    residence_type,
    avg_glucose_level,
    hypertensiv_status,
    bmi,
    smoking_status, stroke_status):

    """
    Validate patient assessment form data.
    Raise ValueError if there is an error.
    """

    if not all([work_type, ever_married, residence_type,
                hypertensiv_status, smoking_status, stroke_status]):
        raise ValueError("Please fill out all required fields.")

    # allowed values for category fields
    allowed_work_types = {"private", "self employed", "govt job",
                          "never worked", "children"}
    if work_type not in allowed_work_types:
        raise ValueError("Invalid work type selected.")

    allowed_ever_married = {"yes", "no"}
    if ever_married not in allowed_ever_married:
        raise ValueError("Invalid marital status selected.")

    allowed_residence = {"urban", "rural"}
    if residence_type not in allowed_residence:
        raise ValueError("Invalid residence type selected.")

    allowed_hypertension = {"0", "1"}
    if hypertensiv_status not in allowed_hypertension:
        raise ValueError("Invalid hypertension status selected.")
    
    allowed_stroke_status = {"0", "1"}
    if stroke_status not in allowed_stroke_status:
        raise ValueError("Invalid stroke status selected.")

    allowed_smoking = {"formerly smoked", "never smoked",
                       "smokes", "unknown"}
    if smoking_status not in allowed_smoking:
        raise ValueError("Invalid smoking status selected.")

    try:
        avg_glucose_level = float(avg_glucose_level)
        bmi = float(bmi)
    except ValueError:
        raise ValueError("Average glucose level and BMI must be valid numbers.")

    if not (40 <= avg_glucose_level <= 400):
        raise ValueError("Average glucose level should be between 40 and 400 mg/dL.")

    if not (10 <= bmi <= 80):
        raise ValueError("BMI should be between 10 and 80.")

    return {
        "work_type": work_type,
        "ever_married": ever_married,
        "residence_type": residence_type,
        "avg_glucose_level": avg_glucose_level,
        "hypertensiv_status": hypertensiv_status,
        "bmi": bmi,
        "smoking_status": smoking_status,
        "stroke_status": stroke_status,
    }

def get_patient_assessments_history(assessment, patient_id):
    """
    Fetch all assessments for a given patient from the database.
    """
    if assessment is not None:
        assessments = assessment.find({"patient_id": patient_id}).sort("date", -1)
        return list(assessments)
    return []

def validate_emergency_contact_data(first_name, last_name, phone_number, relationship):
    """
    Validate emergency contact data.
    Raises ValueError with appropriate message if validation fails.
    """
    # Validate required fields
    if not all([first_name, last_name, phone_number, relationship]):
        raise ValueError("All fields are required.")
    
    # Validate phone number format
    phone_pattern = r'^\+?[1-9]\d{1,14}$'
    if not re.match(phone_pattern, phone_number):
        raise ValueError("Please enter a valid phone number (e.g., +1234567890).")
    
    # Validate relationship is one of the allowed values
    allowed_relationships = ['parent', 'brother', 'sister', 'family friend', 'friend', 'spouse']
    if relationship.lower() not in allowed_relationships:
        raise ValueError("Invalid relationship type selected.")