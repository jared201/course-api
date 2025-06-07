#!/usr/bin/env python3
"""
Test script to create 5 student accounts and 5 instructor accounts.

Prerequisites:
1. Make sure Redis server is running. You can start it with:
   - On macOS: `brew services start redis` or `redis-server /usr/local/etc/redis.conf`
   - On Linux: `sudo service redis-server start` or `redis-server`
   - On Windows: Start Redis server from the installation directory

2. Set Redis connection environment variables if needed:
   - REDIS_HOST: Redis server hostname or IP address (default: localhost)
   - REDIS_PORT: Redis server port (default: 6379)
   - REDIS_PASSWORD: Redis server password (if required)

3. To run in mock mode (without Redis):
   - MOCK_MODE=1 python create_test_accounts.py

Example:
   REDIS_HOST=localhost REDIS_PORT=6379 python create_test_accounts.py
"""
import asyncio
import sys
import os
from services import User, UserRole, UserService

# Mock UserService class for testing without Redis
class MockUserService:
    def __init__(self):
        self.users = []
        self.next_id = 1

    async def create_user(self, user_data):
        # Assign ID if not provided
        if "id" not in user_data or user_data["id"] is None:
            user_data["id"] = self.next_id
            self.next_id += 1

        user = User(**user_data)
        self.users.append(user)
        return user

    async def list_users(self):
        return self.users

async def create_test_accounts():
    """Create test student and instructor accounts."""
    try:
        # Check if we should use mock mode
        mock_mode = os.environ.get("MOCK_MODE", "0") == "1"

        if mock_mode:
            print("Running in MOCK MODE (without Redis)")
            user_service = MockUserService()
        else:
            user_service = UserService()

            # Check if Redis is connected
            if not user_service.redis_client:
                print("Error: Could not connect to Redis. Make sure Redis server is running.")
                print("You can run in mock mode with: MOCK_MODE=1 python create_test_accounts.py")
                return

        print("Creating 5 student accounts...")
        student_accounts = []
        for i in range(1, 6):
            student_data = {
                "username": f"student{i}",
                "email": f"student{i}@example.com",
                "full_name": f"Student {i}",
                "password": "password123",  # In a real app, use secure passwords
                "role": UserRole.STUDENT,
                "id": i  # Use integer IDs
            }
            try:
                student = await user_service.create_user(student_data)
                student_accounts.append(student)
                print(f"Created student account: {student.username} ({student.email})")
            except Exception as e:
                print(f"Error creating student{i}: {e}")

        print("\nCreating 5 instructor accounts...")
        instructor_accounts = []
        for i in range(1, 6):
            instructor_data = {
                "username": f"instructor{i}",
                "email": f"instructor{i}@example.com",
                "full_name": f"Instructor {i}",
                "password": "password123",  # In a real app, use secure passwords
                "role": UserRole.INSTRUCTOR,
                "id": i + 100  # Use integer IDs with offset to avoid conflicts
            }
            try:
                instructor = await user_service.create_user(instructor_data)
                instructor_accounts.append(instructor)
                print(f"Created instructor account: {instructor.username} ({instructor.email})")
            except Exception as e:
                print(f"Error creating instructor{i}: {e}")

        print("\nVerifying accounts...")
        all_users = await user_service.list_users()
        print(f"Total users in database: {len(all_users)}")

        # Count students and instructors
        students = [user for user in all_users if user.role == UserRole.STUDENT]
        instructors = [user for user in all_users if user.role == UserRole.INSTRUCTOR]

        print(f"Number of student accounts: {len(students)}")
        print(f"Number of instructor accounts: {len(instructors)}")

        print("\nTest account creation completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
        return

if __name__ == "__main__":
    try:
        asyncio.run(create_test_accounts())
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
    except Exception as e:
        print(f"Unhandled exception: {e}")
        sys.exit(1)
