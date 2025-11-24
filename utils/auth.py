from functools import wraps
from flask import session, redirect, url_for, flash
from models.users import db, User, RoleTypes
import re
from models.employee import Employee


def auth_required(f):
    
    # This is a reusable decorator that requires authentication for routes.
    # It checks if user_id exists in session, redirects to login if not authenticated.
    
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for('login'))
        
        # If the user is authenticated it proceeds with the original function
        return f(*args, **kwargs)
    
    return decorated

def handle_login(email, password):
    """Handle user login logic"""
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['email'] = user.email
        # Get first_name and last_name from Employee table through relationship
        session['first_name'] = user.employee.first_name if user.employee else 'Unknown'
        session['last_name'] = user.employee.last_name if user.employee else 'User'
        session['role'] = user.employee.role if user.employee else None
        return True
    return False

def get_user_redirect_by_role():
    """Get redirect URL based on user role"""
    role = session.get('role', '').lower()
    if role == RoleTypes.SUPER_ADMIN:
        return url_for('users_management')
    elif role == RoleTypes.DOCTOR:
        return url_for('patient_management')
    elif role == RoleTypes.NURSE:
        return url_for('patient_management')
    return url_for('login')

def validate_registration_data(employee_id, email, password):
    """Validate registration form data - returns error message or None if valid"""
    
    # Basic validation
    if not employee_id or not email or not password:
        return 'Please fill out all required fields'
    
    # Employee ID pattern validation (6 alphanumeric characters)
    if len(employee_id) != 6 or not employee_id.isalnum():
        return 'Employee ID must be exactly 6 alphanumeric characters'
    
    # Email pattern validation
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_pattern, email):
        return 'Please enter a valid email address'
    
    # Password strength validation
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,}$'
    if not re.match(pattern, password):
        return 'Password must be 8+ chars and include upper, lower, digit and special char.'
    
    return None

def validate_credentials(employee_id, email):
    """Validate if employee_id and email exist together in Employee table"""
    employee = Employee.query.filter_by(employee_id=employee_id, email=email).first()
    if not employee:
        return 'Employee ID and email do not match our records. Please contact admin.'
    
    """Check if user already exists """
      # Check if email already exists in User table
    if User.query.filter_by(email=email).first():
        return 'Email already registered. Please use a different email.'
        
    # Check if employee_id already registered in User table
    if User.query.filter_by(employee_id=employee_id).first():
        return 'Employee ID already registered. Please use a different Employee ID.'
    
    return None


def create_user(employee_id, email, password):
    """Create a new user"""
    user = User(
        employee_id=employee_id,
        email=email
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    return user


def store_form_data_in_session(employee_id, email):
    """Store form data in session for persistence"""
    session['form_data'] = {
        'employee_id': employee_id,
        'email': email
    }
    
def get_and_clear_form_data():
    """Get form data from session and clear it (one-time use)"""
    form_data = session.get('form_data', {})
    session.pop('form_data', None)
    return form_data