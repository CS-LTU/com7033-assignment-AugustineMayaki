from flask import Flask, render_template, session, request, redirect, url_for, flash
from utils.decorators import auth_required, admin_required, doctor_required, admin_or_doctor_required
from utils.patients import get_patients_statistics
from utils.patients import(register_patient, validate_patient_data, update_patient, get_patient_by_id, get_all_patients, delete_patient)
from utils.auth import get_current_user


def init_patient_routes(app):
    @app.route("/patient-management")
    @auth_required
    @admin_or_doctor_required
    def patient_management():
        current_user = get_current_user()
        return render_template('pages/patient_management.html', 
                             patients_overview=get_patients_statistics(), 
                             patients=get_all_patients(),
                             current_user=current_user)
    
    @app.route("/register-patient", methods=['GET', 'POST'])
    @auth_required
    @admin_required
    def register_patient_route():
        if request.method == 'POST':
            try:
                first_name = request.form.get('first_name', '').strip()
                last_name = request.form.get('last_name', '').strip()
                date_of_birth = request.form.get('date_of_birth', '').strip()
                email = request.form.get('email', '').strip()
                gender = request.form.get('gender', '').strip()
                
                validate_patient_data(email, date_of_birth, gender)
                
                register_patient(first_name, last_name, email, date_of_birth, gender)
                flash('Patient registration successful!', 'success')
                return redirect(url_for('patient_management'))
            
            except ValueError as err:
                flash(str(err), 'error')
                return redirect(url_for('patient_management'))
        
        # GET request - show registration form
        return render_template('pages/patient_management.html', patients_overview=get_patients_statistics(), patients=get_all_patients())
            
    @app.route("/patient-management/patient/<int:patient_id>")
    @auth_required
    @doctor_required
    def patient_info(patient_id):
        patient = get_patient_by_id(patient_id)
        if not patient:
            flash("Patient not found.", "error")
            return redirect(url_for('patient_management'))
        
        return render_template('pages/patient_info.html', patient=patient)