from flask import Flask, render_template, session, request, redirect, url_for, flash
from utils.decorators import auth_required, admin_required, doctor_required, admin_or_doctor_required
from utils.patients import get_patients_statistics
from utils.patients import(register_patient, validate_patient_data, validate_patient_assessment_data, update_patient, get_patient_by_id, get_all_patients, delete_patient, get_patient_assessments_history)


def init_patient_routes(app, db=None, patient_assessments_collection=None):
    @app.route("/patient-management")
    @auth_required
    @admin_or_doctor_required
    def patient_management():
        return render_template('pages/patient_management.html', 
                             patients_overview=get_patients_statistics(patient_assessments_collection), 
                             patients=get_all_patients())
    
    
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
        
        assessments = get_patient_assessments_history(patient_assessments_collection, patient_id)
        return render_template('pages/patient_info.html', patient=patient, assessments=assessments)
    
    
    @app.route("/patient-management/patient/<int:patient_id>/update", methods=['GET', 'POST'])
    @auth_required
    @doctor_required
    def update_patient_route(patient_id):
        if request.method == 'POST':
            try:
                first_name = request.form.get('first_name', '').strip()
                last_name = request.form.get('last_name', '').strip()
                date_of_birth = request.form.get('date_of_birth', '').strip()
                gender = request.form.get('gender', '').strip()
                
                validate_patient_data(date_of_birth=date_of_birth, gender=gender)
                update_patient(patient_id, first_name, last_name, date_of_birth, gender)
                flash('Patient information updated successfully!', 'success')
                return redirect(url_for('patient_info', patient_id=patient_id))
            
            except ValueError as err:
                flash(str(err), 'error')
                return redirect(url_for('patient_info', patient_id=patient_id))
    
    
    @app.route("/patient-management/patient/<int:patient_id>/delete", methods=['POST'])
    @auth_required
    @admin_required
    def delete_patient_route(patient_id):
        try:
            delete_patient(patient_id)
            flash('Patient deleted successfully!', 'success')
        except Exception as e:
            flash('Failed to delete patient.', 'error')
        return redirect(url_for('patient_management'))
    
    
    @app.route("/patient-management/patient/<int:patient_id>/assessments", methods=['POST'])
    @auth_required
    @doctor_required
    def run_patient_assessment(patient_id):
        patient = get_patient_by_id(patient_id)
        if not patient:
            flash("Patient not found.", "error")
            return redirect(url_for('patient_management'))
        
        try:
            work_type = request.form.get('work_type', '').strip()
            ever_married = request.form.get('ever_married', '').strip()
            residence_type = request.form.get('residence_type', '').strip()
            avg_glucose_level = float(request.form.get('avg_glucose_level', '0').strip())
            hypertensiv_status = request.form.get('hypertensiv_status').strip()
            bmi = float(request.form.get('bmi', '0').strip())
            smoking_status = request.form.get('smoking_status', '').strip()
            
            result = validate_patient_assessment_data(
                work_type=work_type,
                ever_married=ever_married,
                residence_type=residence_type,
                avg_glucose_level=avg_glucose_level,
                hypertensiv_status=hypertensiv_status,
                bmi=bmi,
                smoking_status=smoking_status
            )
            
            new_assessment = {
                "patient_id": patient_id,
                **result
            }
            
            patient_assessments_collection.insert_one(new_assessment)
            flash('Patient assessment recorded successfully!', 'success')
            return redirect(url_for('patient_info', patient_id=patient_id))
            
        except ValueError as err:
            flash(str(err), 'error')

            return redirect(url_for('patient_info', patient_id=patient_id))
            
        
        