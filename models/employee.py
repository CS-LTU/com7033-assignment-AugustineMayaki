import sqlite3
from utils.init_db import db_name

def init_employee():
    """
    Create the employee table.
    """
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()
    
    # Create the employee table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employee (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

class Employee:
    """
    A class to represent.
    """
    def __init__(self, employee_id, first_name, last_name, email, role, created_at=None):
        self.employee_id = employee_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.role = role
        self.created_at = created_at
