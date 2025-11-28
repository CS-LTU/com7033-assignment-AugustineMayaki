import sqlite3

def db_name():
    """Return the database file path as string"""
    return 'instance/neuroPredict.db'

def get_db_connection():
    """Get a database connection"""
    return sqlite3.connect(db_name())
