"""User service handling user creation, authentication, and database retrieval."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password


class UserService:
    """Encapsulates business logic for User operations."""

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Fetch a user by primary key ID."""
        return db.get(User, user_id)

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Fetch a user by email address (case-insensitive)."""
        statement = select(User).where(User.email == email.lower().strip())
        return db.scalars(statement).first()

    @classmethod
    def create_user(cls, db: Session, user_in: UserCreate) -> User:
        """Create and persist a new user with hashed password."""
        hashed_pwd = hash_password(user_in.password)
        db_user = User(
            email=user_in.email.lower().strip(),
            full_name=user_in.full_name,
            hashed_password=hashed_pwd,
            is_active=True,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @classmethod
    def authenticate(cls, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user against email and password.

        Returns User if credentials match, else None.
        """
        user = cls.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


user_service = UserService()
