from flask import Flask, render_template, session
import os
from utils.decorators import auth_required, admin_required
from utils.users import get_users_overview, get_all_users, get_user_count
from utils.patients import get_patients_overview
from routes.auth_routes import init_auth_routes
from routes.user_routes import init_user_routes

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
 

init_auth_routes(app)
init_user_routes(app)

@app.route("/patient-management")
@auth_required
def patient_management():
    return render_template('pages/patient_management.html', patients_overview=get_patients_overview(), user=session)



    


if __name__=='__main__':
    app.run(debug=True)