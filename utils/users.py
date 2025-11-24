from models.users import db, User

def get_users_overview():
    """Get users overview statistics"""
    total_users = db.session.query(User).count()
    users_overview = [
        {
            "label": "Total Users",
            "value": total_users,
            "description": "Total registered users in the system"
        },
    ]
    return users_overview

def get_all_users():
    """Get all users with employee information ordered by creation date"""
    return db.session.query(User).order_by(User.created_at.desc()).all()

def get_user_count():
    """Get total number of users"""
    return db.session.query(User).count()
