
from flask import flash, render_template, request, redirect, session, url_for 
from utils.auth import (
    handle_login, redirect_user_by_role, validate_registration_data,
    validate_credentials, create_user, clear_form_data
)


def init_auth_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            
            if handle_login(email, password):
                flash("Login successfully", "success")
                return redirect(redirect_user_by_role())
            else:
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