"""Authentication endpoints for user registration, login, and current user profile."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.schemas.auth import Token, LoginRequest
from app.services.user_service import user_service
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description="Validates email, checks for duplicates, securely hashes the password, and creates the user.",
)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    """Register a new user."""
    existing_user = user_service.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists.",
        )
    user = user_service.create_user(db, user_in=user_in)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate user and issue access token",
    description="Authenticates credentials and returns a JWT Bearer access token. Supports both JSON payload and OAuth2 form data.",
)
async def login(
    request: Request,
    db: Session = Depends(get_db),
) -> Token:
    """Authenticate user credentials and generate JWT token."""
    content_type = request.headers.get("content-type", "").lower()
    email = None
    password = None

    if "application/json" in content_type:
        try:
            body = await request.json()
            email = body.get("email") or body.get("username")
            password = body.get("password")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload provided.",
            )
    else:
        # Fallback to form data for Swagger UI OAuth2 Authorize flow
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both email and password are required.",
        )

    user = user_service.authenticate(db, email=str(email), password=str(password))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive.",
        )

    access_token = create_access_token(subject=str(user.id))
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user profile",
    description="Retrieves the profile information for the authenticated user without exposing password hashes.",
)
def read_current_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Return profile of the currently logged-in user."""
    return current_user
