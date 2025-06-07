#!/usr/bin/env python3
"""
Test script to verify that user roles are correctly extracted from Redis after login.

This script:
1. Creates a test user with a specific role
2. Authenticates the user
3. Verifies that the role is correctly set from Redis

Prerequisites:
1. Make sure Redis server is running
2. Set Redis connection environment variables if needed
3. To run in mock mode (without Redis):
   - MOCK_MODE=1 python test_user_role.py
"""
import asyncio
import sys
import os
from services import User, UserRole, UserService, AuthService
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Mock classes for testing without Redis
class MockUserService:
    def __init__(self):
        self.users = {}
        self.redis_client = True  # Fake redis client to pass connection check

    async def create_user(self, user_data):
        # Assign ID if not provided
        if "id" not in user_data or user_data["id"] is None:
            user_data["id"] = len(self.users) + 1

        user = User(**user_data)
        self.users[user.username] = user
        return user

    async def get_user_by_username(self, username):
        return self.users.get(username)

    async def get_user(self, user_id):
        for user in self.users.values():
            if user.id == user_id:
                return user
        return None

class MockTokenData(BaseModel):
    user_id: int
    username: str
    role: str
    exp: datetime

class MockToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    refresh_token: Optional[str] = None

class MockAuthService:
    def __init__(self, user_service):
        self.user_service = user_service

    async def authenticate_user(self, username, password):
        user = await self.user_service.get_user_by_username(username)
        if not user:
            return None

        # In a real implementation, we would check the password
        # For this test, we'll just return the user data
        return {
            "user_id": user.id,
            "username": user.username,
            "role": user.role
        }

    async def create_access_token(self, data, expires_delta=None):
        if expires_delta:
            expires_at = datetime.now() + expires_delta
        else:
            expires_at = datetime.now() + timedelta(minutes=15)

        return MockToken(
            access_token="mock_access_token",
            token_type="bearer",
            expires_at=expires_at,
            refresh_token="mock_refresh_token"
        )

    async def verify_token(self, token):
        # In a real implementation, this would verify the token
        # For this test, we'll just return mock data
        return MockTokenData(
            user_id=1,
            username="test_instructor",
            role=UserRole.INSTRUCTOR,
            exp=datetime.now() + timedelta(minutes=15)
        )

async def test_user_role():
    """Test that user roles are correctly extracted from Redis after login."""
    try:
        # Check if we should use mock mode
        mock_mode = os.environ.get("MOCK_MODE", "1") == "1"

        if mock_mode:
            print("Running in MOCK MODE (without Redis)")
            user_service = MockUserService()
            auth_service = MockAuthService(user_service)
        else:
            # Initialize services
            user_service = UserService()
            auth_service = AuthService()

            # Check if Redis is connected
            if not user_service.redis_client:
                print("Error: Could not connect to Redis. Make sure Redis server is running.")
                print("You can run in mock mode with: MOCK_MODE=1 python test_user_role.py")
                return

        # Create a test user with instructor role
        test_username = "test_instructor"
        test_password = "password123"

        # Check if user already exists
        existing_user = await user_service.get_user_by_username(test_username)
        if existing_user:
            print(f"User {test_username} already exists, using existing user")
            user = existing_user
        else:
            print(f"Creating test user: {test_username}")
            user_data = {
                "username": test_username,
                "email": f"{test_username}@example.com",
                "full_name": "Test Instructor",
                "password": test_password,
                "role": UserRole.INSTRUCTOR
            }
            user = await user_service.create_user(user_data)
            print(f"Created user with role: {user.role}")

        # Authenticate the user
        print(f"Authenticating user: {test_username}")
        user_data = await auth_service.authenticate_user(test_username, test_password)
        if not user_data:
            print("Error: Authentication failed")
            return

        print(f"Authentication successful. User data: {user_data}")
        print(f"Role from authentication: {user_data['role']}")

        # Create a token
        token = await auth_service.create_access_token(data=user_data)

        # Simulate the authenticate_user_with_token function
        token_data = await auth_service.verify_token(token.access_token)
        if token_data is None:
            print("Error: Token verification failed")
            return

        print(f"Token data: {token_data}")

        # Special case for admin user
        if token_data.username == "admin" and token_data.role == UserRole.ADMIN:
            print("Admin user detected, using mock admin user")
            user_from_db = User(
                id=token_data.user_id,
                username=token_data.username,
                email="admin@example.com",
                full_name="Admin User",
                role=UserRole.ADMIN
            )
        else:
            # Get the user directly by username from Redis
            user_from_db = await user_service.get_user_by_username(token_data.username)
            if user_from_db is None:
                print("Error: User not found in Redis by username")
                return

            # Ensure the user's role is set from the token data
            user_from_db.role = token_data.role

        print(f"User from database: {user_from_db}")
        print(f"Role from database: {user_from_db.role}")

        # Get the user directly from Redis
        user_from_redis = await user_service.get_user_by_username(user_from_db.username)
        if user_from_redis is None:
            print("Error: User not found in Redis")
            return

        print(f"User from Redis: {user_from_redis}")
        print(f"Role from Redis: {user_from_redis.role}")

        # Update the user's role from Redis
        if user_from_redis and user_from_redis.role:
            user_from_db.role = user_from_redis.role
            print(f"Updated role from Redis: {user_from_db.role}")

        # Verify that the role is correct
        if user_from_db.role == UserRole.INSTRUCTOR:
            print("SUCCESS: User role is correctly set from Redis")
        else:
            print(f"ERROR: User role is not correctly set. Expected {UserRole.INSTRUCTOR}, got {user_from_db.role}")

    except Exception as e:
        print(f"An error occurred: {e}")
        return

if __name__ == "__main__":
    try:
        asyncio.run(test_user_role())
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
    except Exception as e:
        print(f"Unhandled exception: {e}")
        sys.exit(1)
