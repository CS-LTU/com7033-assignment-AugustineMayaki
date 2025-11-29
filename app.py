from flask import Flask
import os
from routes.auth_routes import init_auth_routes
from routes.user_routes import init_user_routes
from routes.patient_routes import init_patient_routes

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
 

init_auth_routes(app)
init_user_routes(app)
init_patient_routes(app)


    


if __name__=='__main__':
    app.run(debug=True)