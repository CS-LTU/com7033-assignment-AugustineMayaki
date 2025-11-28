import csv
import os
from models.users import init_users
from models.roles import init_roles
from models.employee import init_employee, Employee
import sqlite3
from utils.init_db import db_name

def delete_and_create_database():
    """
    Drop and recreate the database tables.
    """
    # Create instance directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()
    
    # Drop tables if exist 
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS employee")
    cursor.execute("DROP TABLE IF EXISTS roles")

    conn.commit()
    conn.close()  
    
    # Recreate tables individually
    init_roles()
    init_employee()
    init_users()

def seed_database():
    print("Deleting and recreating database...")
    delete_and_create_database()
    print("Tables created.")
    
    print("Seeding database with initial data...")
    # Open database connection
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()
    
    print("Creating employees from CSV...")
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
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()