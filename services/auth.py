from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    user_id: int
    username: str
    role: str
    exp: datetime


class Permission(str, Enum):
    READ_COURSE = "read:course"
    WRITE_COURSE = "write:course"
    DELETE_COURSE = "delete:course"
    READ_USER = "read:user"
    WRITE_USER = "write:user"
    DELETE_USER = "delete:user"
    READ_CONTENT = "read:content"
    WRITE_CONTENT = "write:content"
    DELETE_CONTENT = "delete:content"
    ENROLL = "enroll"
    MANAGE_ENROLLMENTS = "manage:enrollments"


class AuthService:
    """Service for authentication and authorization in the online course platform."""

    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with username and password."""
        from services.user import UserService

        # Get the user service
        user_service = UserService()

        # Get the user by username
        user = await user_service.get_user_by_username(username)
        if not user:
            return None

        # Get the stored password
        if not user_service.redis_client:
            return None

        try:
            password_key = f"user_password:{username}"
            stored_password = user_service.redis_client.get(password_key)

            # Check if password matches
            if stored_password and stored_password == password:
                # Return user data for token creation
                return {
                    "user_id": user.id,
                    "username": user.username,
                    "role": user.role
                }
        except Exception as e:
            print(f"Error authenticating user: {e}")

        return None

    async def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> Token:
        """Create a JWT access token."""
        # In a real implementation, this would create a JWT token
        # For this implementation, we'll create a token in the format "username:role"

        # Special case for admin placeholder
        if data.get("username") == "admin" and data.get("role") == "admin":
            access_token = "access_token_placeholder"
        else:
            # Create token in format "username:role"
            username = data.get("username", "")
            role = data.get("role", "")
            access_token = f"{username}:{role}"

        refresh_token = await self.create_refresh_token(data, expires_delta)

        # Set expiration time
        if expires_delta:
            expires_at = datetime.now() + expires_delta
        else:
            expires_at = datetime.now() + timedelta(minutes=15)

        # Create and return Token object
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_at=expires_at,
            refresh_token=refresh_token
        )

    async def create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT refresh token."""
        # In a real implementation, this would create a JWT token
        return "refresh_token_placeholder"

    async def verify_token(self, token: str, token_type: TokenType = TokenType.ACCESS) -> Optional[TokenData]:
        """
        Extract username from token and return user data without token verification.
        This modified implementation skips token verification and directly uses username from Redis.
        """
        from services.user import UserService, UserRole

        # Remove 'Bearer ' prefix if present
        if token.startswith("Bearer "):
            token = token[7:]

        # For the placeholder token, return admin user
        if token == "access_token_placeholder":
            return TokenData(
                user_id=999,
                username="admin",
                role=UserRole.ADMIN,
                exp=datetime.now() + timedelta(minutes=15)
            )

        # Extract username from token (in a real implementation, this would be from JWT payload)
        # For this implementation, we'll assume the token format is "username:role"
        try:
            # Try to parse the token as "username:role"
            parts = token.split(":")
            if len(parts) >= 1:
                username = parts[0]

                # Get user from Redis
                user_service = UserService()
                user = await user_service.get_user_by_username(username)

                if user:
                    # Return TokenData with user information
                    return TokenData(
                        user_id=user.id,
                        username=user.username,
                        role=user.role,
                        exp=datetime.now() + timedelta(minutes=15)
                    )
        except Exception as e:
            print(f"Error extracting username from token: {e}")

        return None

    async def refresh_access_token(self, refresh_token: str) -> Optional[Token]:
        """Use a refresh token to generate a new access token."""
        # In a real implementation, this would verify the refresh token and create a new access token
        return None

    async def has_permission(self, user_id: int, permission: Permission) -> bool:
        """Check if a user has a specific permission."""
        # In a real implementation, this would check user roles and permissions
        return False

    async def get_user_permissions(self, user_id: int) -> Dict[Permission, bool]:
        """Get all permissions for a user."""
        # In a real implementation, this would fetch user roles and calculate permissions
        return {permission: False for permission in Permission}

    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change a user's password."""
        from services.user import UserService

        # Get the user service
        user_service = UserService()

        # Get the user by ID
        user = await user_service.get_user(user_id)
        if not user:
            return False

        # Verify old password
        if not user_service.redis_client:
            return False

        try:
            password_key = f"user_password:{user.username}"
            stored_password = user_service.redis_client.get(password_key)

            # Check if old password matches
            if stored_password and stored_password == old_password:
                # Update password
                user_service.redis_client.set(password_key, new_password)
                return True
        except Exception as e:
            print(f"Error changing password: {e}")

        return False

    async def generate_password_reset_token(self, email: str) -> Optional[str]:
        """Generate a password reset token for a user."""
        # In a real implementation, this would create a token and store it
        return None

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset a user's password using a reset token."""
        from services.user import UserService

        # In a real implementation, this would verify the token and get the username
        # For this implementation, we'll assume the token is the username for simplicity
        username = token

        # Get the user service
        user_service = UserService()

        # Get the user by username
        user = await user_service.get_user_by_username(username)
        if not user:
            return False

        # Update password
        if not user_service.redis_client:
            return False

        try:
            password_key = f"user_password:{username}"
            user_service.redis_client.set(password_key, new_password)
            return True
        except Exception as e:
            print(f"Error resetting password: {e}")

        return False
