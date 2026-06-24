import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.orm import Session
from app.models import User

# Security configuration
ph = PasswordHasher()

# Get or generate secret key
SECRET_KEY = os.getenv("AUTH_SECRET_KEY") or secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))  # 8 hours


class AuthService:
    """Service for authentication and JWT handling."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using Argon2."""
        return ph.hash(password)

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        try:
            ph.verify(password_hash, password)
            return True
        except VerifyMismatchError:
            return False

    @staticmethod
    def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token for a user.

        Args:
            user: User object
            expires_delta: Custom expiration time (default: 8 hours)

        Returns:
            JWT token string
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        expire = datetime.utcnow() + expires_delta

        to_encode = {
            "sub": str(user.id),
            "username": user.username,
            "display_name": user.display_name,
            "role": user.role,
            "exp": expire
        }

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        """
        Decode and verify a JWT token.

        Args:
            token: JWT token string

        Returns:
            Token payload dict or None if invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    def get_user_from_token(token: str, db: Session) -> Optional[User]:
        """
        Extract user from token and fetch from database.

        Args:
            token: JWT token
            db: Database session

        Returns:
            User object or None if token invalid or user not found
        """
        payload = AuthService.decode_access_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        try:
            user = db.query(User).filter(User.id == int(user_id), User.is_active == True).first()
            return user
        except Exception:
            return None

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password.

        Args:
            db: Database session
            username: Username
            password: Password (plain text)

        Returns:
            User object if successful, None otherwise
        """
        user = db.query(User).filter(User.username == username, User.is_active == True).first()

        if not user:
            return None

        if not AuthService.verify_password(password, user.password_hash):
            return None

        return user

    @staticmethod
    def get_permission_for_role(role: str) -> dict:
        """
        Get permissions for a given role.

        Args:
            role: User role (admin, operator, viewer)

        Returns:
            Dictionary of permissions
        """
        permissions = {
            "admin": {
                "create_team": True,
                "edit_team": True,
                "delete_team": True,
                "ocr_upload": True,
                "batch_ocr": True,
                "create_player": True,
                "edit_player": True,
                "verify_player": True,
                "reject_player": True,
                "delete_player": True,
                "export_xlsx": True,
                "view_audit_logs": True,
                "cleanup_system": True,
                "manage_users": True,
            },
            "operator": {
                "create_team": True,
                "edit_team": True,
                "delete_team": False,
                "ocr_upload": True,
                "batch_ocr": True,
                "create_player": True,
                "edit_player": True,
                "verify_player": True,
                "reject_player": True,
                "delete_player": False,
                "export_xlsx": True,
                "view_audit_logs": True,  # Only their team's logs
                "cleanup_system": False,
                "manage_users": False,
            },
            "viewer": {
                "create_team": False,
                "edit_team": False,
                "delete_team": False,
                "ocr_upload": False,
                "batch_ocr": False,
                "create_player": False,
                "edit_player": False,
                "verify_player": False,
                "reject_player": False,
                "delete_player": False,
                "export_xlsx": False,
                "view_audit_logs": False,
                "cleanup_system": False,
                "manage_users": False,
            }
        }

        return permissions.get(role, permissions["viewer"])

    @staticmethod
    def can_perform(role: str, action: str) -> bool:
        """
        Check if a role can perform an action.

        Args:
            role: User role
            action: Action name

        Returns:
            True if allowed, False otherwise
        """
        permissions = AuthService.get_permission_for_role(role)
        return permissions.get(action, False)
