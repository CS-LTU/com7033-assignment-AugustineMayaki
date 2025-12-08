import csv
import os
from models.users import init_users
from models.roles import init_roles
from models.patients import init_patients_demographics
from models.employee import init_employee
import sqlite3
from utils.init_db import db_name
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()

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

def delete_database():
    """
    Drop the database tables.
    """
    # Create instance directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()
    
    # Drop tables if exist 
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS employee")
    cursor.execute("DROP TABLE IF EXISTS roles")
    cursor.execute("DROP TABLE IF EXISTS patients_demographics")
    

    conn.commit()
    conn.close()  


def init_database():
    init_roles()
    init_employee()
    init_users()
    init_patients_demographics()
    
    print("Seeding database with initial data...")
    # Open database connection
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()
    
    print("Creating employees from CSV.....")
    csv_file = 'employees.csv'
        
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
        print("employees.csv not found, skipping.")
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def create_new_table_only():
    """
    Create only the new patients_demographics table without touching existing tables.
    """
    
    # Create instance directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()
    
    # Drop tables if exist 
    print("Dropping existing patients_demographics table if it exists...")
    cursor.execute("DROP TABLE IF EXISTS patients_demographics")
    

    conn.commit()
    conn.close()  
    print("Creating new patients_demographics table...")
    init_patients_demographics()
    print("patients_demographics table created successfully!")

if __name__ == '__main__':
    # create_new_table_only()
      
    init_database()