#!/usr/bin/env python3
"""
Test script to remove all test accounts.

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
   - MOCK_MODE=1 python remove_test_accounts.py

Example:
   REDIS_HOST=localhost REDIS_PORT=6379 python remove_test_accounts.py
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
        
    async def delete_user(self, user_id):
        for i, user in enumerate(self.users):
            if user.id == user_id:
                self.users.pop(i)
                return True
        return False

async def remove_test_accounts():
    """Remove all test student and instructor accounts."""
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
                print("You can run in mock mode with: MOCK_MODE=1 python remove_test_accounts.py")
                return

        print("Retrieving all users...")
        all_users = await user_service.list_users()
        print(f"Total users in database before removal: {len(all_users)}")

        # Count students and instructors
        students = [user for user in all_users if user.role == UserRole.STUDENT]
        instructors = [user for user in all_users if user.role == UserRole.INSTRUCTOR]

        print(f"Number of student accounts: {len(students)}")
        print(f"Number of instructor accounts: {len(instructors)}")

        # Identify test accounts (students with IDs 1-5 and instructors with IDs 101-105)
        test_student_ids = list(range(1, 6))
        test_instructor_ids = list(range(101, 106))
        test_account_ids = test_student_ids + test_instructor_ids

        # Remove test accounts
        print("\nRemoving test accounts...")
        removed_count = 0
        for user_id in test_account_ids:
            try:
                success = await user_service.delete_user(user_id)
                if success:
                    removed_count += 1
                    print(f"Removed account with ID: {user_id}")
                else:
                    print(f"Account with ID {user_id} not found or could not be removed")
            except Exception as e:
                print(f"Error removing account with ID {user_id}: {e}")

        print(f"\nRemoved {removed_count} test accounts")

        # Verify accounts were removed
        print("\nVerifying accounts removal...")
        remaining_users = await user_service.list_users()
        print(f"Total users in database after removal: {len(remaining_users)}")

        # Count remaining students and instructors
        remaining_students = [user for user in remaining_users if user.role == UserRole.STUDENT]
        remaining_instructors = [user for user in remaining_users if user.role == UserRole.INSTRUCTOR]

        print(f"Number of remaining student accounts: {len(remaining_students)}")
        print(f"Number of remaining instructor accounts: {len(remaining_instructors)}")

        # Check if any test accounts still exist
        remaining_test_accounts = [user for user in remaining_users if user.id in test_account_ids]
        if remaining_test_accounts:
            print("\nWarning: Some test accounts could not be removed:")
            for user in remaining_test_accounts:
                print(f"  - ID: {user.id}, Username: {user.username}, Role: {user.role}")
        else:
            print("\nAll test accounts were successfully removed!")

    except Exception as e:
        print(f"An error occurred: {e}")
        return

if __name__ == "__main__":
    try:
        asyncio.run(remove_test_accounts())
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
    except Exception as e:
        print(f"Unhandled exception: {e}")
        sys.exit(1)