import csv
import os
import sqlite3
from datetime import datetime, date
import random
import pandas as pd
from models.users import init_users
from models.roles import init_roles
from models.patients import init_patients_demographics
from models.employee import init_employee
from utils.init_db import db_name
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


#  MONGO CONNECTION
def get_mongo_connection():
    """
    Get MongoDB connection
    Returns db and collections if successful, else None.
    """
    try:
        client = MongoClient(os.environ.get("MONGODB_URI"))
        db = client[os.environ.get("MONGODB_NAME")]
        patient_assessments_collection = db[os.environ.get("MONGODB_PATIENT_ASSESSMENTS_COLLECTION")]
        emergency_contact_coll = db[os.environ.get("MONGODB_EMERGENCY_CONTACT_COLL")]

        print("Connected to MongoDB")
        return db, patient_assessments_collection, emergency_contact_coll

    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return None, None, None


def dob_from_age(age: float) -> str:
    """
    Rough DOB estimate based on age.
    
    Returns ISO format date string."""
    year = datetime.now().year - int(age)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return date(year, month, day).isoformat()

# RESET DATABASE

def delete_database():
    os.makedirs('instance', exist_ok=True)

    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS employee")
    cursor.execute("DROP TABLE IF EXISTS roles")
    cursor.execute("DROP TABLE IF EXISTS patients_demographics")

    conn.commit()
    conn.close()



#  INIT DATABASE

def init_database():
    init_roles()
    init_employee()
    init_users()
    init_patients_demographics()

    print("Seeding database with initial data...")

    # SQLITE CONNECTION 
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()

    #  MONGO CONNECTION
    db, patient_assessments_collection, _ = get_mongo_connection()


    #  SEED EMPLOYEES FROM CSV
 
    print("Creating employees from CSV.....")
    csv_file = 'csv/employees.csv'

    if os.path.exists(csv_file):
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            inserted = 0
            skipped = 0

            for row in reader:
                employee_id = row["employee_id"].strip()
                first = row["first_name"].strip()
                last = row["last_name"].strip()
                email = row["email"].strip()
                role = row["role"].strip()

                cursor.execute("""
                    INSERT OR IGNORE INTO employee (employee_id, first_name, last_name, email, role)
                    VALUES (?, ?, ?, ?, ?)
                """, (employee_id, first, last, email, role))
                if cursor.rowcount == 1:
                    inserted += 1
                else:
                    skipped += 1

            print(f"{inserted} employees inserted.")
            print(f"{skipped} duplicates skipped.")
    else:
        print("csv/employees.csv not found, skipping.")

    
    #  SEED PATIENT DEMOGRAPHICS and ASSESSMENTS FROM HEALTH DATASET
    
    print("\n Seeding patient demographics + assessments from CSV...")

    PATIENT_CSV = "csv/healthcare_dataset_stroke_with_names.csv"

    if os.path.exists(PATIENT_CSV):
        df = pd.read_csv(PATIENT_CSV)

        sqlite_inserted = 0
        mongo_inserted = 0
        skipped = 0

        for _, row in df.iterrows():
            csv_source_id = int(row["id"])  # original dataset row id

            # SQLite Insert
            first_name = row["first_name"]
            last_name = row["last_name"]
            email = row["email"]
            gender = row["gender"]
            age = row["age"]
            date_of_birth = dob_from_age(age)

            # Check if patient already exists by email or source_row_id
            cursor.execute(
                "SELECT id FROM patients_demographics WHERE email = ? OR source_row_id = ?",
                (email, csv_source_id)
            )
            existing = cursor.fetchone()

            if existing:
                patient_id = existing[0]
                skipped += 1
            else:
                cursor.execute(
                    """
                    INSERT INTO patients_demographics
                        (first_name, last_name, email, date_of_birth, gender, source_row_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (first_name, last_name, email, date_of_birth, gender, csv_source_id),
                )

                patient_id = cursor.lastrowid
                sqlite_inserted += 1

            # Mongo Insert check if assessment already exists for this source_row_id
            existing_assessment = patient_assessments_collection.find_one({
                "source_row_id": csv_source_id
            })

            if not existing_assessment:
                bmi = row.get("bmi")
                bmi_clean = None if pd.isna(bmi) else float(bmi)

                assessment_doc = {
                    "patient_id": patient_id,
                    "source_row_id": csv_source_id,

                    "work_type": row.get("work_type"),
                    "ever_married": row.get("ever_married"),
                    "residence_type": row.get("Residence_type"),
                    "avg_glucose_level": float(row["avg_glucose_level"]),
                    "hypertensiv_status": int(row["hypertension"]),
                    "bmi": bmi_clean,
                    "smoking_status": row.get("smoking_status"),
                    "heart_disease": int(row["heart_disease"]),
                    "stroke_status": row.get("smoking_status"),
                }

                patient_assessments_collection.insert_one(assessment_doc)
                mongo_inserted += 1

        print(f"SQLite: {sqlite_inserted} patients inserted, {skipped} duplicates skipped.")
        print(f" MongoDB: {mongo_inserted} assessments inserted.")

    else:
        print(f"{PATIENT_CSV} not found skipping health seeding.")

    conn.commit()
    conn.close()

    print("\n Database initialized & seeded successfully!")


if __name__ == '__main__':
    init_database()