from app import app
from models.users import db, User, Role, RoleTypes
from werkzeug.security import generate_password_hash

def seed_user():
    with app.app_context():
        Role.create_default_roles()
        
        # Get the super admin role
        super_admin = Role.query.filter_by(role_name=RoleTypes.SUPER_ADMIN).first()
        
        super_admin = User(
            first_name="Super",
            last_name="Admin",
            email="superadmin@example.com",
            password=generate_password_hash("@Admin123", method='pbkdf2:sha256'),
            role_id=super_admin.id 
        )
        
        db.session.add(super_admin)
        db.session.commit()
        print("Super admin user created successfully!")
    
    
if __name__ == '__main__':
    seed_user()