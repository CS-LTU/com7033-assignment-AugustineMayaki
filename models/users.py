import sqlite3
from utils.init_db import db_name
from werkzeug.security import generate_password_hash, check_password_hash
from constants.role_types import RoleTypes

def init_users():
    """
    Create the users table.
    """
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (    
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
    )
    ''')

    conn.commit()
    conn.close()

class User:
    """
    A class to represent the user and perform user-related operations.
    """
    def __init__(self, id, employee_id, email, password_hash=None, is_active=True):
        self.id = id
        self.employee_id = employee_id
        self.email = email
        self.password_hash = password_hash
        self.is_active = bool(is_active)
        self._role = None  # Cache for role from Employee table
        
   
    # Password management methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def get_role(self):
        """
        Get user role from Employee table
        """
        if self._role is None:  # Only query the db if the role is not already cached
        
            conn = sqlite3.connect(db_name())
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT role FROM employee WHERE employee_id = ?''', (self.employee_id,))
            result = cursor.fetchone()
            conn.close()
        
            if result:
                self._role = result[0]  # Cache the role
        
        return self._role 
    
    # User role-checking methods
    def is_super_admin(self):
        role = self.get_role()
        return role and role.lower() == RoleTypes.SUPER_ADMIN

    def is_doctor(self):
        role = self.get_role()
        return role and role.lower() == RoleTypes.DOCTOR

    def is_nurse(self):
        role = self.get_role()
        return role and role.lower() == RoleTypes.NURSE
    
    def is_account_active(self):
        return self.is_active