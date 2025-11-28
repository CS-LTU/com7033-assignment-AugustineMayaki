from flask import Flask, flash, render_template, request, redirect, session, url_for 
import os
from datetime import datetime
from utils.auth import auth_required
from utils.auth import (
    handle_login, redirect_user_by_role, validate_registration_data,
    validate_credentials, create_user, clear_form_data
)
from utils.users import get_users_overview, get_all_users, get_user_count
from utils.patients import get_patients_overview

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

@app.template_filter('format_datetime')
def format_datetime(date_string):
    """Format datetime string to readable format like '20th March at 11:25'"""
    if not date_string:
        return 'N/A'
    
    try:
        # Parse SQLite datetime string
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        
        # Get day with suffix (1st, 2nd, 3rd, 4th, etc.)
        day = dt.day
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        
        # Format: "20th March at 11:25"
        return f"{day}{suffix} {dt.strftime('%B')} at {dt.strftime('%H:%M')}"
    except:
        return date_string  # Return original if parsing fails
 

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if handle_login(email, password):
            flash("Login successfully", "success")
            return redirect(redirect_user_by_role())
        else:
            flash('Invalid email or password', 'error')
            return render_template('pages/auth/login.html', email=email)
    
    return render_template('pages/auth/login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST': 
        session['form_data'] = {
            'employee_id': request.form.get('employee_id', '').strip(),
            'email': request.form.get('email', '').strip()
        }
             
        try:
            employee_id = request.form.get('employee_id', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
       
            validate_registration_data(employee_id, email, password)

            validate_credentials(employee_id, email)
            
            create_user(employee_id, email, password)
            
            # Clear form data on successful registration
            session.pop('form_data', None)
            
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('login'))
        
        except ValueError as err:
            # Handle validation errors raised from the inner functions
            flash(str(err), 'error')
            return redirect(url_for('register'))

        except Exception as e:
            flash('An unexpected error occurred. Please try again.', 'error')
            return redirect(url_for('register'))
        
    # for GET request - gets form data from session if available
    form_data = clear_form_data()
    return render_template('pages/auth/register.html', form_data=form_data)


@app.route("/forgot-password")
def forgot_password():
    return render_template('pages/auth/forgot_password.html')

@app.route("/verify-mfa", methods=['GET', 'POST'])
def verify_mfa():
    return render_template('pages/auth/verify.html')

@app.route("/set_password")
def set_password():
    return render_template('pages/auth/set_password.html')

@app.route("/logout")
def logout():
    session.clear() 
    flash("You have logged out successfuly", "info")
    return redirect(url_for('login'))

@app.route("/patient-management")
@auth_required
def patient_management():
    return render_template('pages/patient_management.html', patients_overview=get_patients_overview(), user=session)


@app.route("/users-management")
@auth_required
def users_management():
    users = get_all_users()
    total_users = get_user_count()
    users_overview = get_users_overview()
    
    return render_template('pages/users_management.html', 
                         user_count=total_users, 
                         users=users, 
                         users_overview=users_overview)



    


if __name__=='__main__':
    app.run(debug=True)