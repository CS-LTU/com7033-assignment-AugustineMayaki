from flask import Flask, flash, render_template, request, redirect, session, url_for 
from models.users import db
import os
from utils.auth import auth_required
from utils.auth import (
    handle_login, get_user_redirect_by_role, validate_registration_data,
    validate_credentials, create_user,
    store_form_data_in_session, get_and_clear_form_data
)
from utils.users import get_users_overview, get_all_users, get_user_count
from utils.patients import get_patients_overview

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///neuroPredict.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
 

db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if handle_login(email, password):
            flash("Login successfully", "success")
            return redirect(get_user_redirect_by_role())
        else:
            flash('Invalid email or password', 'error')
            return render_template('pages/auth/login.html', email=email)
    
    return render_template('pages/auth/login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Store form data in session for persistence
        store_form_data_in_session(employee_id, email)
        
        # Validate registration data
        error = validate_registration_data(employee_id, email, password)
        if error:
            flash(error, 'error')
            return redirect(url_for('register'))
        
        # Check if credentials are valid
        error = validate_credentials(employee_id, email)
        if error:
            flash(error, 'error')
            return redirect(url_for('register'))
        
        # Create the user
        create_user(employee_id, email, password)
        
        # Clear form data on successful registration
        session.pop('form_data', None)
        
        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('login'))
    
    # for GET request - gets form data from session if available
    form_data = get_and_clear_form_data()
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