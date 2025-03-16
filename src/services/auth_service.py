from typing import Optional
from repositories.user_repository import UserRepository, User
from models.database_models import UserRole
from exceptions import ValidationError

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.current_user: Optional[User] = None

    def login(self, username: str, password: str) -> bool:
        """Authenticate user and set current user."""
        if self.user_repository.verify_password(username, password):
            user = self.user_repository.get_by_username(username)
            # Check if user is active
            if user and hasattr(user, 'is_active') and not user.is_active:
                return False
            self.current_user = user
            return True
        return False

    def logout(self) -> None:
        """Clear current user session."""
        self.current_user = None

    def register(self, username: str, email: str, password: str, role: UserRole = UserRole.PASSENGER) -> None:
        """Register a new user."""
        if self.user_repository.get_by_username(username):
            raise ValidationError("Username already exists")

        user = User(id=0, username=username, email=email, role=role)
        self.user_repository.add(user, password)

    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated."""
        return self.current_user is not None

    def require_auth(self) -> None:
        """Raise an error if no user is authenticated."""
        if not self.is_authenticated():
            raise ValidationError("Authentication required")

    def require_role(self, required_role: UserRole) -> None:
        """Check if current user has the required role."""
        self.require_auth()
        if self.current_user.role != required_role:
            raise ValidationError(f"Access denied. {required_role.value} role required.")

    def get_current_user(self) -> Optional[User]:
        """Get the currently authenticated user."""
        return self.current_user

    def get_all_users(self) -> list[User]:
        """Get all users (admin only)."""
        self.require_role(UserRole.ADMIN)
        return self.user_repository.get_all()

    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account (admin only)."""
        self.require_role(UserRole.ADMIN)
        
        # Prevent self-deactivation
        if str(self.current_user.id) == user_id:
            raise ValidationError("Cannot deactivate your own account")
            
        return self.user_repository.delete(user_id)

    def get_user_by_id(self, user_id: int):
        """Get a user by ID."""
        return self.user_repository.get(user_id) 