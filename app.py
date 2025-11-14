from flask import Flask, flash, render_template, request, redirect, session, url_for 
from models.users import db, User
import os

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
            session['first_name'] = user.first_name
            session['last_name'] = user.last_name
            session['role'] = user.role.role_name if user.role else None
            
            # Redirect user to different page based on their role
            if user.is_super_admin():
                flash("Login successfully", "success")
                return redirect(url_for('patient_management'))
            elif user.is_doctor():
                print("Doctor logged in")
                return redirect(url_for('patient_management')) 
            elif user.is_nurse():
                print("Nurse logged in")
                return redirect(url_for('patient_management'))
        else:
            flash('Invalid email or password', 'error')
            return render_template('pages/auth/login.html', email=email)  # Do not pass password
    
    return render_template('pages/auth/login.html')

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
    return redirect(url_for('login'))

@app.route("/patient-management")
def patient_management():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('pages/patient_management.html', patients_overview=PATIENTS_OVERVIEW, user=session)


print(  "Starting the Flask application..."  )


if __name__=='__main__':
    app.run(debug=True)