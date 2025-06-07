#!/usr/bin/env python3
"""
Test script to verify the registration functionality.

Prerequisites:
1. Make sure Redis server is running.
2. Set Redis connection environment variables if needed.

Example:
   python test_registration.py
"""
import asyncio
import os
from services import User, UserRole, UserService
from services.redis_manager import RedisManager

async def test_registration():
    """Test the registration functionality."""
    try:
        # Create a user service
        user_service = UserService()

        # Check if Redis is connected
        if not user_service.redis_client:
            print("Error: Could not connect to Redis. Make sure Redis server is running.")
            return

        # Simulate registration form data
        username = "testregister"
        email = "testregister@example.com"
        full_name = "Test Register User"
        password = "testpassword123"
        role = "student"  # This comes as a string from the form

        # Check if user already exists
        existing_user = await user_service.get_user_by_username(username)
        if existing_user:
            print(f"User {username} already exists. Deleting...")
            await user_service.delete_user(existing_user.id)
            print(f"Deleted existing user: {username}")

        print(f"Registering new user: {username} ({email})...")
        
        # Prepare user data for creation (same structure as in the registration handler)
        user_data = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "password": password,
            "role": role
        }
        
        # Create the user
        user = await user_service.create_user(user_data)
        print(f"Successfully registered user: {user.username} ({user.email})")

        # Verify that the user and password are stored in Redis
        redis_manager = RedisManager()
        redis_client = redis_manager.get_client()
        
        if redis_client:
            # Check user data
            user_key = f"user:{user.username}"
            stored_user = redis_client.get(user_key)
            
            if stored_user:
                print(f"User data is stored in Redis with key: {user_key}")
            else:
                print(f"Error: User data not found in Redis with key: {user_key}")
            
            # Check password
            password_key = f"user_password:{user.username}"
            stored_password = redis_client.get(password_key)
            
            if stored_password:
                print(f"Password is stored in Redis with key: {password_key}")
            else:
                print(f"Error: Password not found in Redis with key: {password_key}")
        
        # Clean up - delete the test user
        print("\nCleaning up - deleting test user...")
        deleted = await user_service.delete_user(user.id)
        if deleted:
            print(f"Deleted test user: {user.username}")
        else:
            print(f"Error deleting test user: {user.username}")
            
        print("\nTest completed.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(test_registration())
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
    except Exception as e:
        print(f"Unhandled exception: {e}")