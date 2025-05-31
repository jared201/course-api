from typing import List, Optional
from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime


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
    
    async def create_user(self, user_data: dict) -> User:
        """Create a new user."""
        user = User(**user_data)
        # In a real implementation, this would save to a database
        return user
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        # In a real implementation, this would fetch from a database
        return None
    
    async def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        """Update a user's information."""
        # In a real implementation, this would update in a database
        return None
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        # In a real implementation, this would delete from a database
        return True
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List all users with pagination."""
        # In a real implementation, this would fetch from a database
        return []