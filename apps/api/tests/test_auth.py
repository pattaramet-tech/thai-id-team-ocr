"""Tests for authentication service."""
import pytest
from app.services.auth import AuthService
from app.models import User
from sqlalchemy.orm import Session


class TestAuthService:
    """Test authentication service."""

    def test_hash_and_verify_password(self):
        """Hash and verify password works."""
        password = "test_password_123"
        hashed = AuthService.hash_password(password)

        assert hashed != password
        assert AuthService.verify_password(password, hashed)
        assert not AuthService.verify_password("wrong_password", hashed)

    def test_create_access_token(self, db_session):
        """Create access token for user."""
        user = User(
            username="testuser",
            display_name="Test User",
            password_hash=AuthService.hash_password("password"),
            role="admin"
        )
        db_session.add(user)
        db_session.commit()

        token = AuthService.create_access_token(user)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self, db_session):
        """Decode and verify token payload."""
        user = User(
            username="testuser",
            display_name="Test User",
            password_hash=AuthService.hash_password("password"),
            role="admin"
        )
        db_session.add(user)
        db_session.commit()

        token = AuthService.create_access_token(user)
        payload = AuthService.decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == str(user.id)
        assert payload["username"] == "testuser"
        assert payload["role"] == "admin"

    def test_decode_invalid_token(self):
        """Invalid token returns None."""
        payload = AuthService.decode_access_token("invalid_token")
        assert payload is None

    def test_get_user_from_token(self, db_session):
        """Get user from valid token."""
        user = User(
            username="testuser",
            display_name="Test User",
            password_hash=AuthService.hash_password("password"),
            role="admin",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        token = AuthService.create_access_token(user)
        retrieved_user = AuthService.get_user_from_token(token, db_session)

        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.username == "testuser"

    def test_get_user_from_invalid_token(self, db_session):
        """Invalid token returns None."""
        user = AuthService.get_user_from_token("invalid_token", db_session)
        assert user is None

    def test_get_user_from_inactive_user(self, db_session):
        """Inactive user cannot use token."""
        user = User(
            username="testuser",
            display_name="Test User",
            password_hash=AuthService.hash_password("password"),
            role="admin",
            is_active=False
        )
        db_session.add(user)
        db_session.commit()

        token = AuthService.create_access_token(user)
        retrieved_user = AuthService.get_user_from_token(token, db_session)

        assert retrieved_user is None

    def test_authenticate_user_success(self, db_session):
        """Authenticate user with correct password."""
        user = User(
            username="testuser",
            display_name="Test User",
            password_hash=AuthService.hash_password("password123"),
            role="admin",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        authenticated = AuthService.authenticate_user(db_session, "testuser", "password123")

        assert authenticated is not None
        assert authenticated.id == user.id

    def test_authenticate_user_wrong_password(self, db_session):
        """Authenticate fails with wrong password."""
        user = User(
            username="testuser",
            display_name="Test User",
            password_hash=AuthService.hash_password("password123"),
            role="admin",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        authenticated = AuthService.authenticate_user(db_session, "testuser", "wrong")

        assert authenticated is None

    def test_authenticate_user_not_found(self, db_session):
        """Authenticate fails for non-existent user."""
        authenticated = AuthService.authenticate_user(db_session, "nonexistent", "password")
        assert authenticated is None

    def test_authenticate_inactive_user(self, db_session):
        """Authenticate fails for inactive user."""
        user = User(
            username="testuser",
            display_name="Test User",
            password_hash=AuthService.hash_password("password123"),
            role="admin",
            is_active=False
        )
        db_session.add(user)
        db_session.commit()

        authenticated = AuthService.authenticate_user(db_session, "testuser", "password123")

        assert authenticated is None

    def test_admin_permissions(self):
        """Admin has all permissions."""
        assert AuthService.can_perform("admin", "create_team")
        assert AuthService.can_perform("admin", "delete_player")
        assert AuthService.can_perform("admin", "manage_users")
        assert AuthService.can_perform("admin", "cleanup_system")

    def test_operator_permissions(self):
        """Operator has limited permissions."""
        assert AuthService.can_perform("operator", "create_team")
        assert AuthService.can_perform("operator", "verify_player")
        assert not AuthService.can_perform("operator", "manage_users")
        assert not AuthService.can_perform("operator", "cleanup_system")

    def test_viewer_permissions(self):
        """Viewer has minimal permissions."""
        assert not AuthService.can_perform("viewer", "create_team")
        assert not AuthService.can_perform("viewer", "edit_player")
        assert not AuthService.can_perform("viewer", "verify_player")
        assert not AuthService.can_perform("viewer", "manage_users")

    def test_get_permission_for_role(self):
        """Get full permission dict for role."""
        admin_perms = AuthService.get_permission_for_role("admin")
        assert admin_perms["create_team"] is True
        assert admin_perms["manage_users"] is True

        viewer_perms = AuthService.get_permission_for_role("viewer")
        assert viewer_perms["create_team"] is False
        assert viewer_perms["manage_users"] is False
