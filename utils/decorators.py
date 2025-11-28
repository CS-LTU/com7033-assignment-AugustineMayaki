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
