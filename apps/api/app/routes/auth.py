from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models import User
from app.services.auth import AuthService
from app.services.audit import AuditService

router = APIRouter()


def get_token_from_header(authorization: str = Header(None)) -> str:
    """Extract token from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    # Expect "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    return parts[1]


class LoginRequest(BaseModel):
    username: str
    password: str


class BootstrapAdminRequest(BaseModel):
    username: str
    display_name: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with username and password.
    Returns JWT access token.
    """
    user = AuthService.authenticate_user(db, request.username, request.password)

    if not user:
        # Don't reveal if username or password is wrong
        AuditService.log_action(
            db,
            action="login_failed",
            entity_type="auth",
            message=f"Login attempt failed for username: {request.username}",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.add(user)
    db.commit()

    # Log successful login
    AuditService.log_action(
        db,
        action="login_success",
        entity_type="auth",
        message=f"User {user.display_name} logged in",
        actor_name=user.display_name,
    )

    # Create token
    token = AuthService.create_access_token(user)

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.post("/auth/bootstrap-admin", response_model=LoginResponse)
async def bootstrap_admin(request: BootstrapAdminRequest, db: Session = Depends(get_db)):
    """
    Create the first admin user.
    Only works if no users exist in the database.
    """
    # Check if any users exist
    user_count = db.query(User).count()
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users already exist. Cannot bootstrap.",
        )

    # Check username is not empty
    if not request.username or len(request.username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters",
        )

    # Check password strength
    if not request.password or len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )

    # Create admin user
    admin_user = User(
        username=request.username,
        display_name=request.display_name,
        password_hash=AuthService.hash_password(request.password),
        role="admin",
        is_active=True
    )

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    # Log admin creation
    AuditService.log_action(
        db,
        action="bootstrap_admin",
        entity_type="auth",
        message=f"First admin user created: {admin_user.display_name}",
    )

    # Create token
    token = AuthService.create_access_token(admin_user)

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.from_orm(admin_user)
    )


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user.
    Requires valid JWT token in Authorization header.
    """
    user = AuthService.get_user_from_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return UserResponse.from_orm(user)


@router.post("/auth/logout")
async def logout(
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db)
):
    """
    Logout (no-op, token validation happens via get_token_from_header).
    Frontend should clear the token.
    """
    user = AuthService.get_user_from_token(token, db)

    if user:
        AuditService.log_action(
            db,
            action="logout",
            entity_type="auth",
            message=f"User {user.display_name} logged out",
            actor_name=user.display_name,
        )

    return {"status": "logged out"}
