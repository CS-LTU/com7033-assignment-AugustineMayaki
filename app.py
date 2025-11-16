from flask import Flask, flash, render_template, request, redirect, session, url_for 
from models.users import db, User
from models.employee import Employee
from utils.auth import auth_required
import os
import re

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///neuroPredict.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
 

db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()

PATIENTS_OVERVIEW=[
    
    {
        "label": "Total Patients",
        "value": "1,234",
        "description": "Registered patients in the system"
    },
    {
        "label": "Total Users",
        "value": "56",
        "description": "Active users managing data"
    },
    {
        "label": "Total Predictions",
        "value": "3,421",
        "description": "Stroke predictions made"
    }
]


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['email'] = user.email
            # Get first_name and last_name from Employee table through relationship
            session['first_name'] = user.employee.first_name if user.employee else 'Unknown'
            session['last_name'] = user.employee.last_name if user.employee else 'User'
            session['role'] = user.employee.role if user.employee else None
            
            # Redirect user to different page based on their role
            role = session.get('role', '').lower()
            if role == 'super admin':
                flash("Login successfully", "success")
                return redirect(url_for('users_management'))
            elif role == 'doctor':
                print("Doctor logged in")
                return redirect(url_for('patient_management')) 
            elif role == 'nurse':
                print("Nurse logged in")
                return redirect(url_for('patient_management'))
        else:
            flash('Invalid email or password', 'error')
            return render_template('pages/auth/login.html', email=email)  # Do not pass password
    
    return render_template('pages/auth/login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Basic validation
        if not employee_id or not email or not password:
            flash('Please fill out all required fields', 'error')
            return render_template('pages/auth/register.html')
        
        # Employee ID pattern validation (6 alphanumeric characters)
        if len(employee_id) != 6 or not employee_id.isalnum():
            flash('Employee ID must be exactly 6 alphanumeric characters', 'error')
            return render_template('pages/auth/register.html')
        
        # Email pattern validation
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, email):
            flash('Please enter a valid email address', 'error')
            return render_template('pages/auth/register.html')
        
        # Password strength validation
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,}$'
        if not re.match(pattern, password):
            flash("Password must be 8+ chars and include upper, lower, digit and special char.", "error")
            return render_template('pages/auth/register.html')
        
        # Check if employee_id and email exist together in the same row in Employee table
        employee = Employee.query.filter_by(employee_id=employee_id, email=email).first()
        if not employee:
            flash('Employee ID and email do not match our records. Please contact admin.', 'error')
            return render_template('pages/auth/register.html')
        
        # Check if email already exists in User table
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('pages/auth/register.html')
            
        # Check if employee_id already registered in User table
        if User.query.filter_by(employee_id=employee_id).first():
            flash('Employee ID already registered. Please use a different Employee ID.', 'error')
            return render_template('pages/auth/register.html')
        
        # Register the user
        user = User(
            employee_id=employee_id,
            email=email
        )
        user.set_password(password) 
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('pages/auth/register.html')


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
    return render_template('pages/patient_management.html', patients_overview=PATIENTS_OVERVIEW, user=session)


@app.route("/users-management")
@auth_required
def users_management():
    # Get users with employee information
    users = db.session.query(User).order_by(User.created_at.desc()).all()
    total_users = db.session.query(User).count()
    users_overview = [
        {
            "label": "Total Users",
            "value": total_users,
            "description": "Total registered users in the system"
        },
    ]
    
    return render_template('pages/users_management.html', 
                         user_count=total_users, 
                         users=users, 
                         users_overview=users_overview)



    


if __name__=='__main__':
    app.run(debug=True)