import csv
import os
from app import app, db
from models.employee import Employee

def populate_employees():
    with app.app_context():
        db.create_all()
        
         # Read CSV file
        csv_file = 'employees.csv'
        if not os.path.exists(csv_file):
            print("employees.csv file not found!")
            return False
            
        with open('employees.csv', 'r') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                employee = Employee(
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    email=row['email'],
                    employee_id=row['employee_id'],
                    role=row['role']
                )
                
                db.session.add(employee)
        
        db.session.commit()
        print("Employees created successfully!")

if __name__ == '__main__':
    populate_employees()