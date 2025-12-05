from flask import Flask
import os
from dotenv import load_dotenv
from routes.auth_routes import init_auth_routes
from routes.user_routes import init_user_routes
from routes.patient_routes import init_patient_routes
from utils.auth import get_current_user
from datetime import datetime
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")
client = MongoClient(os.environ.get("MONGODB_URI"))
db = client[os.environ.get("MONGODB_NAME")]
patient_assessments_collection = db[os.environ.get("MONGODB_PATIENT_ASSESSMENTS_COLLECTION")]
 
 
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
    Converts date string to '30 Nov • 10:31 PM' format.
    """
    datetime_string = datetime.fromisoformat(date)
    return datetime_string.strftime("%d %b • %I:%M %p")



init_auth_routes(app)
init_user_routes(app)
init_patient_routes(app, db, patient_assessments_collection)


    


if __name__=='__main__':
    app.run(debug=True)