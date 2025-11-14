import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# Define the available roles
class RoleTypes:
    SUPER_ADMIN = 'super admin'
    DOCTOR = 'doctor'
    NURSE = 'nurse'

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    
    @staticmethod
    def create_default_roles():
        # a function to create 3 roles
        roles = [
            RoleTypes.SUPER_ADMIN,
            RoleTypes.DOCTOR,
            RoleTypes.NURSE
        ]
        
        for role_name in roles:
            if not Role.query.filter_by(role_name=role_name).first():
                role = Role(role_name=role_name)
                db.session.add(role)
        
        db.session.commit()
# This is the class model for the user table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)
    role = db.relationship('Role', backref='users', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        if self.password is None:
            return False
        return check_password_hash(self.password, password)
    
    # Functions to check user roles
    def is_super_admin(self):
        return self.role and self.role.role_name == RoleTypes.SUPER_ADMIN
    
    def is_doctor(self):
        return self.role and self.role.role_name == RoleTypes.DOCTOR
    
    def is_nurse(self):
        return self.role and self.role.role_name == RoleTypes.NURSE

   
    