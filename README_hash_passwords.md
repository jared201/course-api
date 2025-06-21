# Password Hashing Script

This script is designed to hash all existing plaintext passwords in Redis for improved security.

## Purpose

The script scans all users in the Redis database and checks if their passwords are already hashed. If a password is stored in plaintext, it will hash it using bcrypt (the same hashing algorithm used by the application) and update it in Redis.

## Prerequisites

- Python 3.6+
- Access to the Redis database used by the application
- The required Python packages (installed via `pip install -r requirements.txt`)

## Usage

Basic usage:

```bash
python hash_passwords.py
```

This will attempt to connect to Redis using the default connection parameters (from environment variables or defaults in the RedisManager class).

### Custom Redis Connection

If your Redis server is running on a different host, port, or requires a password, you can specify these parameters:

```bash
python hash_passwords.py --host redis.example.com --port 6379 --password your_redis_password
```

### Command-line Arguments

- `--host`: Redis host address (default: from environment variable REDIS_HOST or "localhost")
- `--port`: Redis port (default: from environment variable REDIS_PORT or 14345)
- `--password`: Redis password (default: from environment variable REDIS_PASSWORD)

## Output

The script will print information about its progress, including:

- Number of users found in Redis
- Which users' passwords were already hashed
- Which users' passwords were hashed by the script
- Any errors encountered
- A summary of the results

## Example Output

```
Starting password hashing process...
Redis URL: redis://localhost:6379
Successfully connected to Redis database
Found 5 users in Redis.
Password for user admin is already hashed.
Successfully hashed password for user: john_doe
Successfully hashed password for user: jane_smith
No password found for user: test_user
Successfully hashed password for user: instructor1

Password hashing complete!
Total users: 5
Passwords hashed: 3
Already hashed: 1
Errors: 0
```

## Security Note

This script should be run in a secure environment by an administrator. After running the script, it's recommended to verify that authentication still works properly for all users.