import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database_manager import DatabaseManager
from repositories.user_repository import UserRepository, User
from models.database_models import UserRole
from werkzeug.security import generate_password_hash

def create_admin_user(username="admin", email="admin@example.com", password="admin123"):
    """Create an admin user in the database."""
    print(f"Creating admin user: {username}")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Create a session
    with db_manager.get_session() as session:
        # Initialize user repository
        user_repository = UserRepository(session)
        
        # Check if admin user already exists
        existing_user = user_repository.get_by_username(username)
        if existing_user:
            print(f"Admin user '{username}' already exists.")
            return
        
        # Create admin user
        admin_user = User(
            id=0,  # Will be auto-assigned
            username=username,
            email=email,
            role=UserRole.ADMIN
        )
        
        # Add user to database
        user_repository.add(admin_user, password)
        print(f"Admin user '{username}' created successfully.")

if __name__ == "__main__":
    # Get command line arguments
    if len(sys.argv) > 3:
        create_admin_user(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        create_admin_user() 