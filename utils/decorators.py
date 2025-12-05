from functools import wraps
from flask import session, redirect, url_for, flash
from constants.role_types import RoleTypes
from utils.auth import get_current_user


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

def admin_required(f):
    """
    A decorator to ensure that the current user is a super admin.
    Clears session and redirect the user to login page if not authenticated or not a super admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        
        # Check if user exists and is super admin
        if not current_user or not current_user.is_super_admin():
            session.clear()
            flash("Access denied. Super admin privileges required.", "error")
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    """
    A decorator to ensure that the current user is a doctor.
    Clears session and redirect the user to login page if not authenticated or not a doctor.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        
        # Check if user exists and is doctor
        if not current_user or not current_user.is_doctor():
            session.clear()
            flash("Access denied. Doctor privileges required.", "error")
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

def admin_or_doctor_required(f):
    """
    A decorator to ensures that the current user is either a super admin or a doctor.
    Clears session and redirect the user to login page if not authenticated or neither a super admin nor a doctor.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        
        # Check if user exists and is either super admin or doctor
        if not current_user or not (current_user.is_super_admin() or current_user.is_doctor()):
            session.clear()
            flash("Access denied. Super admin or Doctor privileges required.", "error")
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

def doctor_or_nurse_required(f):
    """
    A decorator to ensures that the current user is either a doctor or a nurse.
    Clears session and redirect the user to login page if not authorized.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        
        # Check if user exists and is either a doctor or nurse
        if not current_user or not (current_user.is_doctor() or current_user.is_nurse()):
            session.clear()
            flash("Access denied. Doctor or Nurse privileges required.", "error")
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

def health_professionals_required(f):
    """
    A decorator to ensures that the current user is either a required health care professional.
    Clears session and redirect the user to login page if not authorized.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        
        # Check if user exists and is a health care professional (admin, doctor, nurse)
        if not current_user or not (current_user.is_super_admin() or current_user.is_doctor() or current_user.is_nurse()):
            session.clear()
            flash("Access denied. Health professionals privileges required.", "error")
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function