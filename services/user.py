from typing import List, Optional
from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime
import json
import uuid
from services.redis_manager import RedisManager


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class UserRole(str, Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.STUDENT
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    is_active: bool = True

    class Config:
        orm_mode = True


class UserService:
    """Service for managing users in the online course platform."""

    def __init__(self):
        """Initialize the UserService with Redis connection."""
        # Initialize the Redis manager
        self.redis_manager = RedisManager()
        self.redis_client = self.redis_manager.get_client()

    async def create_user(self, user_data: dict) -> User:
        """Create a new user and store in a Redis database."""
        # Extract password if present
        password = user_data.pop("password", None)

        # Generate a unique ID if not provided
        if "id" not in user_data or user_data["id"] is None:
            user_data["id"] = str(uuid.uuid4())

        user = User(**user_data)

        # Store user in Redis
        if self.redis_client:
            try:
                # Convert user to JSON string using custom encoder for datetime
                user_json = json.dumps(user.dict(), cls=DateTimeEncoder)

                # Store in Redis using username as key
                user_key = f"user:{user.username}"
                self.redis_client.set(user_key, user_json)

                # Also store by email for lookup
                email_key = f"email:{user.email}"
                self.redis_client.set(email_key, user.username)

                # Store password if provided
                if password:
                    password_key = f"user_password:{user.username}"
                    self.redis_client.set(password_key, password)

                # Add to users set
                self.redis_client.sadd("users", user.username)
            except Exception as e:
                print(f"Error storing user in Redis: {e}")

        return user

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        if not self.redis_client:
            return None

        try:
            # In our implementation, we're using username as the primary key
            # So we need to scan through users to find by ID
            all_users = await self.list_users()
            for user in all_users:
                if str(user.id) == str(user_id):
                    return user
            return None
        except Exception as e:
            print(f"Error retrieving user from Redis: {e}")
            return None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        if not self.redis_client:
            return None

        try:
            user_key = f"user:{username}"
            user_json = self.redis_client.get(user_key)
            if user_json:
                user_data = json.loads(user_json)
                return User(**user_data)
            return None
        except Exception as e:
            print(f"Error retrieving user from Redis: {e}")
            return None

    async def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        """Update a user's information."""
        if not self.redis_client:
            return None

        try:
            # Find the user first
            existing_user = await self.get_user(user_id)
            if not existing_user:
                return None

            # Extract password if present
            password = user_data.pop("password", None)

            # Update user data
            updated_data = existing_user.dict()
            updated_data.update(user_data)
            updated_data["updated_at"] = datetime.now()

            # Create updated user
            updated_user = User(**updated_data)

            # Store in Redis
            user_key = f"user:{updated_user.username}"
            self.redis_client.set(user_key, json.dumps(updated_user.dict(), cls=DateTimeEncoder))

            # Update password if provided
            if password:
                password_key = f"user_password:{updated_user.username}"
                self.redis_client.set(password_key, password)

            return updated_user
        except Exception as e:
            print(f"Error updating user in Redis: {e}")
            return None

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        if not self.redis_client:
            return False

        try:
            # Find the user first
            existing_user = await self.get_user(user_id)
            if not existing_user:
                return False

            # Delete from Redis
            user_key = f"user:{existing_user.username}"
            email_key = f"email:{existing_user.email}"
            password_key = f"user_password:{existing_user.username}"

            self.redis_client.delete(user_key)
            self.redis_client.delete(email_key)
            self.redis_client.delete(password_key)
            self.redis_client.srem("users", existing_user.username)

            return True
        except Exception as e:
            print(f"Error deleting user from Redis: {e}")
            return False

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List all users with pagination."""
        if not self.redis_client:
            return []

        try:
            # Get all usernames from the users set
            usernames = self.redis_client.smembers("users")

            users = []
            for username in usernames:
                user_key = f"user:{username}"
                user_json = self.redis_client.get(user_key)
                if user_json:
                    user_data = json.loads(user_json)
                    users.append(User(**user_data))

            # Apply pagination
            return users[skip:skip+limit]
        except Exception as e:
            print(f"Error listing users from Redis: {e}")
            return []
