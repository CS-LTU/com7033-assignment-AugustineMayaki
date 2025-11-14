from models.users import db, User, RoleTypes
from werkzeug.security import generate_password_hash

# Function to seed a default super admin user in the database for login access
def seed_user():
    super_admin = User(
        first_name="Super",
        last_name="Admin",
        email="superadmin@example.com",
        password_hash=generate_password_hash("@Admin123", method="pbkdf2:sha256"),
        role=RoleTypes.SUPER_ADMIN
    )
    
    db.session.adsd(super_admin)
    db.session.commit()
    
if __name__ == '__main__':
    seed_user()