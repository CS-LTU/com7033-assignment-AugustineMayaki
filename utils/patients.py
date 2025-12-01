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
    SELECT id, first_name, last_name, email, date_of_birth, gender, created_at
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
    SELECT id, first_name, last_name, email, date_of_birth, gender, created_at
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
            'created_at': r[6]
        })
    return patients

    
def get_patients_statistics():
    """
    Get statistics about patients_demographics in the system.
    """
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM patients_demographics")
    total_patients = cursor.fetchone()[0]

    conn.close()
    return  [
    {
        "label": "Total Patients",
        "value": total_patients,
        "description": "Registered patients in the system"
    },
    {
        "label": "Total Predictions",
        "value": "3,421",
        "description": "Stroke predictions made"
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
        INSERT INTO patients_demographics (first_name, last_name, email, date_of_birth, gender)
        VALUES (?, ?, ?, ?, ?)
        ''', ( first_name, last_name, email, date_of_birth, gender))
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

def delete_patient(id):
    """
    Delete a patient from the database.
    """
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()
    
    cursor.execute('''
    DELETE FROM patients_demographics
    WHERE id = ?
    ''', (id,))
    
    conn.commit()
    conn.close()
    return True

