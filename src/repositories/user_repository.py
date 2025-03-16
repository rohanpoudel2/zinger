from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.database_models import UserModel, UserRole
from .base_repository import BaseRepository
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, id: int, username: str, email: str, role: UserRole, is_active: bool = True):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.is_active = is_active

class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        self.session = session

    def add(self, user: User, password: str) -> None:
        """Add a new user."""
        user_model = UserModel(
            username=user.username,
            email=user.email,
            password_hash=generate_password_hash(password),
            role=user.role,
            is_active=user.is_active
        )
        self.session.add(user_model)
        self.session.commit()

    def get(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        user_model = self.session.get(UserModel, int(user_id))
        if user_model:
            return User(
                id=user_model.id,
                username=user_model.username,
                email=user_model.email,
                role=user_model.role,
                is_active=user_model.is_active
            )
        return None

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        stmt = select(UserModel).where(UserModel.username == username)
        user_model = self.session.scalar(stmt)
        if user_model:
            return User(
                id=user_model.id,
                username=user_model.username,
                email=user_model.email,
                role=user_model.role,
                is_active=user_model.is_active
            )
        return None

    def verify_password(self, username: str, password: str) -> bool:
        """Verify user password."""
        stmt = select(UserModel).where(UserModel.username == username)
        user_model = self.session.scalar(stmt)
        if user_model:
            return check_password_hash(user_model.password_hash, password)
        return False

    def get_all(self) -> list[User]:
        """Get all users."""
        stmt = select(UserModel)
        return [
            User(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                is_active=user.is_active
            )
            for user in self.session.scalars(stmt)
        ]

    def update(self, user: User) -> None:
        """Update user details."""
        user_model = self.session.get(UserModel, user.id)
        if user_model:
            user_model.username = user.username
            user_model.email = user.email
            user_model.role = user.role
            user_model.is_active = user.is_active
            self.session.commit()

    def delete(self, user_id: str) -> bool:
        """Deactivate a user account instead of deleting it."""
        user_model = self.session.get(UserModel, int(user_id))
        if user_model:
            # Instead of deleting, mark the user as inactive
            user_model.is_active = False
            self.session.commit()
            return True
        return False

    def change_password(self, user_id: int, new_password: str) -> bool:
        """Change user password."""
        user_model = self.session.get(UserModel, user_id)
        if user_model:
            user_model.password_hash = generate_password_hash(new_password)
            self.session.commit()
            return True
        return False 