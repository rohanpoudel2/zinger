from typing import Optional
from repositories.user_repository import UserRepository, User
from models.database_models import UserRole, UserModel
from exceptions import ValidationError, AuthenticationError
from werkzeug.security import check_password_hash
import hashlib
import os

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.current_user = None

    def register(self, username: str, password: str) -> Optional[UserModel]:
        """Register a new user."""
        try:
            # Check if username already exists
            existing_user = self.user_repository.get_by_username(username)
            if existing_user:
                raise ValidationError("Username already exists")
            
            # Create new user with a default email based on username
            user = User(
                id=0,  # Will be set by database
                username=username,
                email=f"{username}@example.com",  # Default email
                role=UserRole.PASSENGER,
                is_active=True
            )
            
            self.user_repository.add_with_password(user, password)
            return self.user_repository.get_by_username(username)
        except Exception as e:
            raise ValidationError(f"Registration failed: {str(e)}")

    def _hash_password(self, password: str) -> str:
        """Hash a password for storing."""
        salt = os.urandom(32)  # 32 bytes = 256 bits
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + ':' + key.hex()

    def _verify_password(self, stored_password: str, provided_password: str) -> bool:
        """Verify a stored password against one provided by user."""
        salt_hex, key_hex = stored_password.split(':')
        salt = bytes.fromhex(salt_hex)
        key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return key.hex() == key_hex

    def login(self, username: str, password: str) -> Optional[UserModel]:
        """Authenticate a user."""
        user = self.user_repository.get_by_username(username)
        if not user:
            return None
            
        if check_password_hash(user.password_hash, password):
            self.current_user = user
            return user
        return None

    def logout(self) -> None:
        """Log out the current user."""
        self.current_user = None

    def get_current_user(self) -> Optional[UserModel]:
        """Get the currently logged in user."""
        return self.current_user

    def require_auth(self) -> None:
        """Require that a user is authenticated."""
        if not self.current_user:
            raise AuthenticationError("Authentication required")

    def require_role(self, role: str) -> None:
        """Require that the current user has a specific role."""
        self.require_auth()
        if self.current_user.role != role:
            raise AuthenticationError(f"Role {role} required")

    def get_user_by_id(self, user_id: int) -> Optional[UserModel]:
        """Get a user by ID."""
        return self.user_repository.get_by_id(user_id)

    def get_all_users(self) -> list[UserModel]:
        """Get all users."""
        return self.user_repository.get_all()

    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account (admin only)."""
        self.require_role(UserRole.ADMIN)
        
        # Prevent self-deactivation
        if str(self.current_user.id) == user_id:
            raise ValidationError("Cannot deactivate your own account")
            
        return self.user_repository.delete(user_id)

    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated."""
        return self.current_user is not None 