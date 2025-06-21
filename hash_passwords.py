import asyncio
import argparse
from services.redis_manager import RedisManager
from services.user import UserService
from passlib.context import CryptContext

async def hash_all_passwords(host=None, port=None, password=None):
    """
    Script to hash all existing passwords of users in Redis.
    This script will:
    1. Connect to Redis
    2. Retrieve all users
    3. Check if their passwords are already hashed
    4. Hash any unhashed passwords and update them in Redis

    Args:
        host (str, optional): Redis host address
        port (int, optional): Redis port
        password (str, optional): Redis password
    """
    print("Starting password hashing process...")

    # Initialize Redis connection with provided parameters
    redis_manager = RedisManager(host=host, port=port, password=password)
    redis_client = redis_manager.get_client()

    if not redis_client:
        print("Failed to connect to Redis. Exiting.")
        return

    # Initialize password hashing context
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Get all usernames from the users set
    try:
        usernames = redis_client.smembers("users")
        print(f"Found {len(usernames)} users in Redis.")

        hashed_count = 0
        already_hashed_count = 0
        error_count = 0

        for username in usernames:
            try:
                # Get the stored password
                password_key = f"user_password:{username}"
                stored_password = redis_client.get(password_key)

                if not stored_password:
                    print(f"No password found for user: {username}")
                    continue

                # Check if the password is already hashed
                # Bcrypt hashed passwords start with $2b$
                if stored_password.startswith('$2'):
                    print(f"Password for user {username} is already hashed.")
                    already_hashed_count += 1
                    continue

                # Hash the password
                hashed_password = pwd_context.hash(stored_password)

                # Update the password in Redis
                redis_client.set(password_key, hashed_password)
                print(f"Successfully hashed password for user: {username}")
                hashed_count += 1

            except Exception as e:
                print(f"Error processing user {username}: {e}")
                error_count += 1

        print("\nPassword hashing complete!")
        print(f"Total users: {len(usernames)}")
        print(f"Passwords hashed: {hashed_count}")
        print(f"Already hashed: {already_hashed_count}")
        print(f"Errors: {error_count}")

    except Exception as e:
        print(f"Error retrieving users from Redis: {e}")

if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Hash all user passwords in Redis')
    parser.add_argument('--host', help='Redis host address (default: from env or localhost)')
    parser.add_argument('--port', type=int, help='Redis port (default: from env or 14345)')
    parser.add_argument('--password', help='Redis password (default: from env)')

    args = parser.parse_args()

    # Run the password hashing function with provided arguments
    asyncio.run(hash_all_passwords(
        host=args.host,
        port=args.port,
        password=args.password
    ))
