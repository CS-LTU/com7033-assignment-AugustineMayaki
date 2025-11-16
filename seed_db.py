import csv
import os
from app import app
from models.users import db, Role
from models.employee import Employee
from werkzeug.security import generate_password_hash

def delete_and_create_database():
    with app.app_context():
        db.drop_all()
        db.create_all()


def seed_database():
    with app.app_context():
        try:
            # Try to query a table to see if database exists
            Role.query.first()
        except:
            delete_and_create_database()
            
        # Ensure tables exist
        db.create_all()
        
        # Create default roles
        Role.create_default_roles()
        
        # Create employees from CSV (if available)
        print("👥 Creating employees from CSV...")
        csv_file = 'employees.csv'
        
        if os.path.exists(csv_file):
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                employee_count = 0
                
                for row in reader:
                    employee_id = row['employee_id'].strip()
                    
                    # Check if employee already exists
                    existing_employee = Employee.query.filter_by(employee_id=employee_id).first()
                    if existing_employee:
                        print(f"⏭️  Employee {employee_id} already exists")
                        continue
                    
                    employee = Employee(
                        first_name=row['first_name'].strip(),
                        last_name=row['last_name'].strip(),
                        email=row['email'].strip(),
                        employee_id=employee_id,
                        role=row['role'].strip()
                    )
                    
                    db.session.add(employee)
                    employee_count += 1
                
                if employee_count > 0:
                    db.session.commit()
                    print(f"✅ {employee_count} employees created successfully!")
                else:
                    print("No new employees to create.")
        else:
            print("employees.csv not found, skipping employee creation")
        
        print(" Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()