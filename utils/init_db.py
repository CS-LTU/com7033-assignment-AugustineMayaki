import sqlite3

def db_name():
    """Return the database file path as string. Ensures 'instance' directory exists."""
    import os
    os.makedirs('instance', exist_ok=True)
    return 'instance/neuroPredict.db'

def get_db_connection():
    """Get a database connection"""
    return sqlite3.connect(db_name())
