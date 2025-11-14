from flask import Flask, render_template
from models.users import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///neuroPredict.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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


@app.route('/')
def login():
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



@app.route("/patient-management")
def patient_management():
    return render_template('pages/patient_management.html', patients_overview=PATIENTS_OVERVIEW)


if __name__=='__main__':
    app.run(debug=True)