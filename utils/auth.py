from functools import wraps
from flask import session, url_for, flash
from models.users import User
import re
import sqlite3
from utils.init_db import db_name
from utils.users import find_user_by_email
from werkzeug.security import generate_password_hash



def handle_login(email, password):
    """
    Find the current user by their email.
    Verify the password using check_password method.
    check of the account is active
    Store only user ID in the session for security.
    """
    current_user = find_user_by_email(email)

    if current_user and current_user.check_password(password):
        # Check if account is active
        if not current_user.is_account_active():
            flash('Your account is inactive, please contact admin', 'error')
            return False 
        
        session['user_id'] = current_user.id
        return True 
    
    flash('Invalid email or password', 'error')
    return False

def get_current_user():
    """
    Get current user object from database using session user_id.
    Returns User object or None if not authenticated.
    """
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            u.id,
            u.employee_id,
            u.email,
            e.first_name,
            e.last_name,
            u.password_hash,
            u.is_active
        FROM users u
        JOIN employee e ON u.employee_id = e.employee_id
        WHERE u.id = ?
    ''', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return User(*row)
    return None


def redirect_user_by_role():
    """
    Redirect the user to the appropriate page based on their role.
    Get role from database via User object methods for security.
    """
    current_user = get_current_user()
    
    if not current_user:
        return url_for('login')
    
    # Use User object methods to check role securely
    if current_user.is_super_admin():
        return url_for('users_management')
    elif current_user.is_doctor():
        return url_for('patient_management')
    elif current_user.is_nurse():
        return url_for('patient_management')
    
    return url_for('login')


def validate_registration_data(employee_id, email, password):
    """
    Validate registration form data.
    """
    # Basic validation
    if not employee_id or not email or not password:
        raise ValueError("Please fill out all required fields")
    
    # Employee ID pattern validation
    if len(employee_id) != 6 or not employee_id.isalnum():
        raise ValueError('Employee ID must be exactly 6 alphanumeric characters')
    
    # Email pattern validation
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_pattern, email):
        raise ValueError('Please enter a valid email address') 
    
    # Password strength validation
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,}$'
    if not re.match(pattern, password):
        raise ValueError('Password must be 8+ chars and include upper, lower, digit and special char.')


def validate_credentials(employee_id, email):
    """
    Validate if employee_id and email exist together in Employee table
    """
    try:        
        conn = sqlite3.connect(db_name())
        cursor = conn.cursor()

        ''' 
        Check if the employee_id and email exist together in the Employee table
        '''
        cursor.execute('''
        SELECT 1
        FROM employee
        WHERE employee_id = ? AND email = ?
        ''', (employee_id, email))
        employee = cursor.fetchone()
        if not employee:
            raise ValueError("Employee ID and email do not match our records. Please contact admin.")
        
        # Check if user already exists in User table by email
        cursor.execute('''
        SELECT 1
        FROM users
        WHERE email = ?
        ''', (email,))
        if cursor.fetchone(): 
            raise ValueError('Email already registered. Please use a different email')
            
    
        # Check if employee_id already registered in User table
        cursor.execute('''
        SELECT 1
        FROM users
        WHERE employee_id = ?
        ''', (employee_id,))
        if cursor.fetchone():  
            raise ValueError('Employee ID already registered. Please use a different Employee ID.')
        
    finally:
        conn.close()

def create_user(employee_id, email, password):
    """
    Create a new user
    """
    
    try:
        conn = sqlite3.connect(db_name())
        cursor = conn.cursor()
        
        password_hash = generate_password_hash(password) 
        # Insert a new user into the database
        cursor.execute('''
        INSERT INTO users (employee_id, email, password_hash, is_active)
        VALUES (?, ?, ?, ?)
        ''', (employee_id, email, password_hash, 1))
        
        conn.commit()
        conn.close()
        return True 

    except sqlite3.IntegrityError:
        flash("User creation failed: Duplicate employee ID or email.", "error")
        return False
    
    except Exception:
        # Handle any unexpected exceptions
        flash("An unexpected error occurred. Please try again.", "error")
        return False

    
def clear_form_data():
    """
    Get form data from session and clear it (one-time use)
    """
    form_data = session.get('form_data', {})
    session.pop('form_data', None)
    return form_data