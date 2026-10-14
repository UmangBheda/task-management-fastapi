"""Database session dependency for FastAPI routes."""

from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure it closes after request processing."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
