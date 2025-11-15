from functools import wraps
from flask import session, redirect, url_for, flash


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