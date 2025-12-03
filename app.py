from flask import Flask
import os
from routes.auth_routes import init_auth_routes
from routes.user_routes import init_user_routes
from routes.patient_routes import init_patient_routes
from utils.auth import get_current_user
from datetime import datetime

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
 
@app.context_processor
def inject_user():
    """
    Make the logged-in User object globally available
    in all templates as 'current_user'.
    """
    user = get_current_user()

    return dict(current_user=user)


@app.template_filter("format_date")
def format_date(date):
    """
    Converts ISO 8601 string to '30 Nov 2025, 10:31 PM' format.
    """
    dt = datetime.fromisoformat(date)
    return dt.strftime("%d %b • %I:%M %p")

init_auth_routes(app)
init_user_routes(app)
init_patient_routes(app)


    


if __name__=='__main__':
    app.run(debug=True)