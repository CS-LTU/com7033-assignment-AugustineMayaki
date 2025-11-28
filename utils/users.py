import sqlite3
from utils.init_db import db_name
from models.users import User

def get_users_overview():
    """Get users overview statistics."""
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
    active_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 0")
    inactive_users = cursor.fetchone()[0]

    conn.close()

    return [
        {
            "label": "Total Users",
            "value": total_users,
            "description": "Total registered users in the system"
        },
        {
            "label": "Active Users",
            "value": active_users,
            "description": "Users with active accounts"
        },
        {
            "label": "Inactive Users",
            "value": inactive_users,
            "description": "Users with inactive accounts"
        }
    ]


def get_all_users():
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            u.id, 
            u.employee_id, 
            u.email, 
            u.created_at, 
            u.is_active,
            e.first_name, 
            e.last_name, 
            e.role
        FROM users AS u
        JOIN employee AS e ON u.employee_id = e.employee_id
        ORDER BY u.created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    users = []

    for r in rows:
        users.append({
            "id": r[0],
            "employee_id": r[1],
            "email": r[2],
            "created_at": r[3],
            "is_active": bool(r[4]),
            "first_name": r[5],
            "last_name": r[6],
            "role": r[7]
        })

    return users


def get_user_count():
    """Get total number of users."""
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    conn.close()
    return count

def find_user_by_email(email):
    """
    Fetch a user from the database using their email address.
    """
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, employee_id, email, password_hash, is_active
    FROM users
    WHERE email = ?
    ''', (email,))
    row = cursor.fetchone() 
    conn.close()

    if row:
        return User(*row)  
    return None 

def deactivate_user(user_id):
    """
    Deactivate a user by setting is_active to False.
    """
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE users
    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (user_id,))
    
    conn.commit()
    conn.close()
    return True

def activate_user(user_id):
    """
    Activate a user by setting is_active to True.
    """
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE users
    SET is_active = 1, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (user_id,))
    
    conn.commit()
    conn.close()
    return True