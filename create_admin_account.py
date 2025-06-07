#!/usr/bin/env python3
"""
Script to create an admin account for testing the Redis endpoint.

Prerequisites:
1. Make sure Redis server is running. You can start it with:
   - On macOS: `brew services start redis` or `redis-server /usr/local/etc/redis.conf`
   - On Linux: `sudo service redis-server start` or `redis-server`
   - On Windows: Start Redis server from the installation directory

2. Set Redis connection environment variables if needed:
   - REDIS_HOST: Redis server hostname or IP address (default: localhost)
   - REDIS_PORT: Redis server port (default: 6379)
   - REDIS_PASSWORD: Redis server password (if required)

Example:
   REDIS_HOST=localhost REDIS_PORT=6379 python create_admin_account.py
"""
import asyncio
import sys
import os
from services import User, UserRole, UserService

async def create_admin_account():
    """Create an admin account for testing."""
    try:
        user_service = UserService()

        # Check if Redis is connected
        if not user_service.redis_client:
            print("Error: Could not connect to Redis. Make sure Redis server is running.")
            return

        print("Creating admin account...")
        admin_data = {
            "username": "admin",
            "email": "admin@example.com",
            "full_name": "Admin User",
            "password": "admin",  # In a real app, use secure passwords
            "role": UserRole.ADMIN,
            "id": 999  # Use a unique ID
        }
        try:
            admin = await user_service.create_user(admin_data)
            print(f"Created admin account: {admin.username} ({admin.email})")
        except Exception as e:
            print(f"Error creating admin account: {e}")

        print("\nVerifying account...")
        all_users = await user_service.list_users()
        
        # Check if admin account exists
        admin_users = [user for user in all_users if user.role == UserRole.ADMIN]
        print(f"Number of admin accounts: {len(admin_users)}")
        
        if len(admin_users) > 0:
            print("\nAdmin account creation completed successfully!")
        else:
            print("\nFailed to create admin account.")
    except Exception as e:
        print(f"An error occurred: {e}")
        return

if __name__ == "__main__":
    try:
        asyncio.run(create_admin_account())
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
    except Exception as e:
        print(f"Unhandled exception: {e}")
        sys.exit(1)