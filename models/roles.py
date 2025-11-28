import sqlite3
from utils.init_db import db_name
from constants.role_types import RoleTypes

def init_roles():
    """
    Create the roles table and insert default roles.
    """
    conn = sqlite3.connect(db_name())
    cursor = conn.cursor()

    # Create roles table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_name TEXT UNIQUE NOT NULL
    )
    ''')

    # Insert default roles if they do not exist
    default_roles = RoleTypes.all_roles()
    for role in default_roles:
        cursor.execute('''
        INSERT OR IGNORE INTO roles (role_name) VALUES (?)
        ''', (role,))

    conn.commit()
    conn.close()