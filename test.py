import unittest
from app import app
import sqlite3
import os

def create_database():
        db_name = 'test_database.db'
        
        if os.path.exists(db_name):
            os.remove(db_name)
        
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL
            )
            ''')
            
        cursor.execute(''' 
                       INSERT INTO users (employee_id, email)
                       VALUES (?, ?)''', ('EMP001', 'augustinemayaki@gmail.com'))
        conn.commit() 
        conn.close()
        
        
def user_in_db(email):
    db_name = 'test_database.db'
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    
    user = cursor.fetchone()
    cursor.close()
    conn.close()
 
    return user is not None

class NeuroPredictTest(unittest.TestCase):
    # set up test client
    
    def setUp(self):
        self.employee_id = "EMP001"
        self.email = "augustinemayaki@gmail.com"
        app.testing =True   #enables testing mode
        self.app = app.test_client()   #initialize test client 
        
    def test_login_page(self):
        response = self.app.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
        self.assertIn(b'Email Address', response.data)
        self.assertIn(b'password', response.data)
        
    def test_register_page(self):
        response = self.app.get('/register')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)
        self.assertIn(b'Employee ID', response.data)
        self.assertIn(b'Email Address', response.data)
        self.assertIn(b'Password', response.data)

    
        
    def test_user_creation(self):
      self.assertTrue(
        user_in_db(self.email),
        f"User with employee_id {self.employee_id} and email {self.email} should exist in the database."
)



create_database()
if __name__ == "__main__":
        unittest.main(verbosity=2)