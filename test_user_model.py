#!/usr/bin/env python3
"""
Simple test script to verify the User model validation.
This script doesn't require Redis to be running.
"""
import asyncio
from services.user import User, UserService

async def test_user_model():
    """Test the User model validation."""
    try:
        # Create a UserService instance
        user_service = UserService()

        # Prepare user data
        user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "full_name": "Test User",
            "password": "password123",
            "role": "student"
        }

        # Create a User object (this will validate the data)
        user = User(**user_data)
        print(f"User created successfully with default ID: {user.id}")

        # Test with our modified create_user method
        # This should generate an integer ID
        user_with_id = await user_service.create_user(user_data)
        print(f"User created with generated ID: {user_with_id.id}")
        print(f"ID type: {type(user_with_id.id)}")

        # Verify it's an integer
        assert isinstance(user_with_id.id, int), "ID is not an integer!"

        print("Test passed! User ID is correctly handled as an integer.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_user_model())
