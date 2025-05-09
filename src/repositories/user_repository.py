from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.database_models import UserModel, UserRole
from .base_repository import BaseRepository
from werkzeug.security import generate_password_hash, check_password_hash
import logging

class User:
    def __init__(self, id: int, username: str, email: str, role: UserRole, is_active: bool = True):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.is_active = is_active

class UserRepository(BaseRepository[UserModel]):
    def __init__(self, session: Session):
        self.session = session

    def add(self, user: UserModel) -> None:
        """Add a new user to the database."""
        self.session.add(user)
        self.session.commit()

    def get(self, id: str) -> Optional[UserModel]:
        """Get a user by ID."""
        try:
            return self.session.query(UserModel).filter(UserModel.id == id).first()
        except Exception as e:
            logging.error(f"Error getting user by ID: {e}")
            return None

    def get_all(self) -> List[UserModel]:
        """Get all users."""
        return self.session.query(UserModel).all()

    def update(self, user: UserModel) -> None:
        """Update a user."""
        self.session.merge(user)
        self.session.commit()

    def delete(self, id: str) -> bool:
        """Delete a user by ID."""
        try:
            user = self.get(id)
            if user:
                self.session.delete(user)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error deleting user: {e}")
            return False

    # Additional methods specific to UserRepository

    def add_with_password(self, user: User, password: str) -> None:
        """Add a new user to the database with password."""
        user_model = UserModel(
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            password_hash=generate_password_hash(password)
        )
        self.add(user_model)

    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        """Get a user by ID."""
        return self.session.query(UserModel).filter_by(id=user_id).first()

    def get_by_username(self, username: str) -> Optional[UserModel]:
        """Get a user by username."""
        return self.session.query(UserModel).filter_by(username=username).first()

    def verify_password(self, username: str, password: str) -> bool:
        """Verify user password."""
        stmt = select(UserModel).where(UserModel.username == username)
        user_model = self.session.scalar(stmt)
        if user_model:
            return check_password_hash(user_model.password_hash, password)
        return False

    def change_password(self, user_id: int, new_password: str) -> bool:
        """Change user password."""
        user_model = self.session.get(UserModel, user_id)
        if user_model:
            user_model.password_hash = generate_password_hash(new_password)
            self.session.commit()
            return True
        return False 