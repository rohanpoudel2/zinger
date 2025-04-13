from typing import Optional
from repositories.user_repository import UserRepository, User
from models.database_models import UserRole, UserModel
from exceptions import ValidationError, AuthenticationError
from utils.auth_utils import verify_password
import hashlib
import os
from views.context.app_context import AppContext

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.context = AppContext()

    def register(self, username: str, email: str, password: str) -> Optional[UserModel]:
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
                email=email,  # Use the provided email
                role=UserRole.PASSENGER,
                is_active=True
            )
            
            self.user_repository.add_with_password(user, password)
            return self.user_repository.get_by_username(username)
        except Exception as e:
            raise ValidationError(f"Registration failed: {str(e)}")

    def login(self, username: str, password: str) -> Optional[UserModel]:
        """Authenticate a user and update AuthStore."""
        user = self.user_repository.get_by_username(username)
        if not user:
            return None
            
        if verify_password(user.password_hash, password):
            # Update AuthStore on successful login
            auth_store = self.context.get_store('auth')
            if auth_store:
                auth_store.update({'current_user': user, 'is_authenticated': True})
            return user
        return None

    def logout(self) -> None:
        """Log out the current user by updating AuthStore."""
        auth_store = self.context.get_store('auth')
        if auth_store:
            auth_store.update({'current_user': None, 'is_authenticated': False})

    def get_current_user(self) -> Optional[UserModel]:
        """Get the currently logged in user from AuthStore."""
        auth_store = self.context.get_store('auth')
        return auth_store.get_state().get('current_user') if auth_store else None

    def require_auth(self) -> None:
        """Require that a user is authenticated based on AuthStore."""
        if not self.is_authenticated():
            raise AuthenticationError("Authentication required")

    def require_role(self, role: str) -> None:
        """Require that the current user has a specific role."""
        self.require_auth()
        current_user = self.get_current_user()
        if not current_user or current_user.role != role:
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
        """Check if a user is currently authenticated based on AuthStore."""
        auth_store = self.context.get_store('auth')
        return auth_store.get_state().get('is_authenticated', False) if auth_store else False 