import sqlite3
from utils.init_db import db_name

def init_patients_demographics():
    """
    Create the patients_demographics table.
    """
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()
    
    # Create the patients_demographics table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients_demographics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        date_of_birth DATE NOT NULL,
        gender TEXT NOT NULL, 
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    
class Patient:
    """
    A class to represent a patient.
    """
    def __init__(self, id, first_name, last_name, email, date_of_birth, gender, created_at=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email  
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.created_at = created_at
        
   