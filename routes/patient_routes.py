from flask import Flask, render_template, request, redirect, url_for, flash
from utils.decorators import auth_required, admin_required, doctor_required, health_professionals_required, doctor_or_nurse_required
from utils.patients import get_patients_statistics
from utils.patients import(register_patient, validate_patient_data, validate_patient_assessment_data, update_patient, get_patient_by_id, get_all_patients, delete_patient, get_patient_assessments_history, validate_emergency_contact_data)
from bson import ObjectId


def init_patient_routes(app, db=None, patient_assessments_collection=None, patient_emergency_contact_collection=None):
    @app.route("/patient-management")
    @auth_required
    @health_professionals_required
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
        return render_template('pages/patient_management.html', patients_overview=get_patients_statistics(patient_assessments_collection), patients=get_all_patients())
            
    @app.route("/patient-management/patient/<int:patient_id>")
    @auth_required
    @doctor_or_nurse_required
    def patient_info(patient_id):
        patient = get_patient_by_id(patient_id)
        if not patient:
            flash("Patient not found.", "error")
            return redirect(url_for('patient_management'))
        
        assessments = get_patient_assessments_history(patient_assessments_collection, patient_id)
        
        # Get emergency contacts for this patient
        emergency_contacts = []
        if patient_emergency_contact_collection is not None:
            emergency_contacts = list(patient_emergency_contact_collection.find({"patient_id": patient_id}))
        
        return render_template('pages/patient_info.html', patient=patient, assessments=assessments, emergency_contacts=emergency_contacts)
    
    
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
            delete_patient(patient_id, assessment_collection=patient_assessments_collection)
            flash('Patient deleted successfully!', 'success')
        except Exception as e:
              flash(f'Failed to delete patient: {e}', 'error')
        return redirect(url_for('patient_management'))
    
    
    @app.route("/patient-management/patient/<int:patient_id>/assessments", methods=['POST'])
    @auth_required
    @doctor_required
    def run_patient_assessment(patient_id):
        patient = get_patient_by_id(patient_id)
        if not patient:
            flash("Patient not found.", "error")
            return redirect(url_for('patient_management'))
        
        # Collect assessment data
        work_type = request.form.get('work_type', '').strip()
        ever_married = request.form.get('ever_married', '').strip()
        residence_type = request.form.get('residence_type', '').strip()
        avg_glucose_level = request.form.get('avg_glucose_level', '').strip()
        hypertensiv_status = request.form.get('hypertensiv_status', '').strip()
        bmi = request.form.get('bmi', '').strip()
        smoking_status = request.form.get('smoking_status', '').strip()
        
        try:
            result = validate_patient_assessment_data(
                work_type=work_type,
                ever_married=ever_married,
                residence_type=residence_type,
                avg_glucose_level=float(avg_glucose_level) if avg_glucose_level else 0,
                hypertensiv_status=hypertensiv_status,
                bmi=float(bmi) if bmi else 0,
                smoking_status=smoking_status
            )
            
            new_assessment = {
                "patient_id": int(patient_id),
                **result
            }
            
            if patient_assessments_collection is not None:
                patient_assessments_collection.insert_one(new_assessment)
            flash('Patient assessment recorded successfully!', 'success')
            return redirect(url_for('patient_info', patient_id=patient_id))
            
        except ValueError as err:
            flash(str(err), 'error')
            # Return to the page with form data preserved
            assessments = get_patient_assessments_history(patient_assessments_collection, patient_id)
            return render_template('pages/patient_info.html', 
                                 patient=patient, 
                                 assessments=assessments,
                                 form_data={
                                     'work_type': work_type,
                                     'ever_married': ever_married,
                                     'residence_type': residence_type,
                                     'avg_glucose_level': avg_glucose_level,
                                     'hypertensiv_status': hypertensiv_status,
                                     'bmi': bmi,
                                     'smoking_status': smoking_status
                                 })
        except Exception as e:
            flash(f'Failed to save assessment: {str(e)}', 'error')
            assessments = get_patient_assessments_history(patient_assessments_collection, patient_id)
            return render_template('pages/patient_info.html', 
                                 patient=patient, 
                                 assessments=assessments,
                                 form_data={
                                     'work_type': work_type,
                                     'ever_married': ever_married,
                                     'residence_type': residence_type,
                                     'avg_glucose_level': avg_glucose_level,
                                     'hypertensiv_status': hypertensiv_status,
                                     'bmi': bmi,
                                     'smoking_status': smoking_status
                                 })
    
    
    # Emergency Contact Routes
    @app.route("/patient-management/patient/<int:patient_id>/emergency-contact/add", methods=['POST'])
    @auth_required
    @doctor_required
    def add_emergency_contact(patient_id):
        patient = get_patient_by_id(patient_id)
        if not patient:
            flash("Patient not found.", "error")
            return redirect(url_for('patient_management'))
        
        try:
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            phone_number = request.form.get('phone_number', '').strip()
            relationship = request.form.get('relationship', '').strip()
            
            validate_emergency_contact_data(first_name, last_name, phone_number, relationship)
            
            new_contact = {
                "patient_id": int(patient_id),
                "first_name": first_name,
                "last_name": last_name,
                "phone_number": phone_number,
                "relationship": relationship
            }
            
            if patient_emergency_contact_collection is not None:
                patient_emergency_contact_collection.insert_one(new_contact)
            
            flash('Emergency contact added successfully!', 'success')
        except ValueError as err:
            flash(str(err), 'error')
        except Exception as e:
            flash(f'Failed to add emergency contact: {str(e)}', 'error')
        
        return redirect(url_for('patient_info', patient_id=patient_id))
    
    
    @app.route("/patient-management/patient/<int:patient_id>/emergency-contact/<contact_id>/update", methods=['POST'])
    @auth_required
    @doctor_required
    def update_emergency_contact(patient_id, contact_id):
        patient = get_patient_by_id(patient_id)
        if not patient:
            flash("Patient not found.", "error")
            return redirect(url_for('patient_management'))
        
        try:
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            phone_number = request.form.get('phone_number', '').strip()
            relationship = request.form.get('relationship', '').strip()
            
            validate_emergency_contact_data(first_name, last_name, phone_number, relationship)
            
            updated_contact = {
                "first_name": first_name,
                "last_name": last_name,
                "phone_number": phone_number,
                "relationship": relationship
            }
            
            if patient_emergency_contact_collection is not None:
            # match both _id AND patient_id
                result = patient_emergency_contact_collection.update_one(
                    {
                        "_id": ObjectId(contact_id),
                        "patient_id": int(patient_id) 
                    },
                    {"$set": updated_contact}
                )
                
                if result.modified_count > 0:
                    flash('Emergency contact updated successfully!', 'success')
                else:
                    flash('No changes were made.', 'info')
        except ValueError as err:
            flash(str(err), 'error')
        except Exception as e:
            flash(f'Failed to update emergency contact: {str(e)}', 'error')
        
        return redirect(url_for('patient_info', patient_id=patient_id))
    
    
    @app.route("/patient-management/patient/<int:patient_id>/emergency-contact/<contact_id>/delete", methods=['POST'])
    @auth_required
    @doctor_required
    def delete_emergency_contact(patient_id, contact_id):
        try:
            if patient_emergency_contact_collection is not None:
                patient_emergency_contact_collection.delete_one({"_id": ObjectId(contact_id)})
            flash('Emergency contact deleted successfully!', 'success')
        except Exception as e:
            flash(f'Failed to delete emergency contact: {str(e)}', 'error')
        
        return redirect(url_for('patient_info', patient_id=patient_id))