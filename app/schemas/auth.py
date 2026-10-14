"""Pydantic schemas for Authentication and JWT Tokens."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Schema for JWT access token response."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for decoded JWT token payload."""
    sub: Optional[str] = None
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    """Schema for user login credentials."""
    email: EmailStr
    password: str = Field(..., min_length=1)
