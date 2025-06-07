import redis
import os
from typing import Optional, Dict, Any


class RedisManager:
    """
    A class for managing Redis connections and operations.
    This class provides a reusable way to connect to Redis and perform common operations.
    """

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, 
                 password: Optional[str] = None, decode_responses: bool = True):
        """
        Initialize the RedisManager with connection parameters.

        Args:
            host: Redis host address. If None, will use REDIS_HOST env var or default.
            port: Redis port. If None, will use REDIS_PORT env var or default.
            password: Redis password. If None, will use REDIS_PASSWORD env var or default.
            decode_responses: Whether to decode Redis responses to strings.
        """
        # Load Redis configuration from environment variables with defaults
        self.redis_host = host or os.getenv("REDIS_HOST", "localhost")
        self.redis_port = port or int(os.getenv("REDIS_PORT", "14345"))
        self.redis_password = password or os.getenv("REDIS_PASSWORD", "")
        self.decode_responses = decode_responses
        self.redis_client = None
        self.connect()

    def connect(self) -> bool:
        """
        Connect to Redis database.

        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            connection_params = {
                "host": self.redis_host,
                "port": self.redis_port,
                "decode_responses": self.decode_responses
            }

            # Add password if provided
            if self.redis_password:
                connection_params["password"] = self.redis_password

            self.redis_client = redis.Redis(**connection_params)

            # Construct and log the Redis URL
            redis_url = f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}" if self.redis_password else f"redis://{self.redis_host}:{self.redis_port}"
            print(f"Redis URL: {redis_url}")

            # Test connection
            self.redis_client.ping()
            print("Successfully connected to Redis database")
            return True
        except redis.ConnectionError as e:
            print(f"Failed to connect to Redis: {e}")
            self.redis_client = None
            return False
        except Exception as e:
            print(f"Unexpected error connecting to Redis: {e}")
            self.redis_client = None
            return False

    def get_client(self) -> Optional[redis.Redis]:
        """
        Get the Redis client instance.

        Returns:
            Optional[redis.Redis]: The Redis client or None if not connected.
        """
        return self.redis_client

    def is_connected(self) -> bool:
        """
        Check if connected to Redis.

        Returns:
            bool: True if connected, False otherwise.
        """
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False

    def set(self, key: str, value: str) -> bool:
        """
        Set a key-value pair in Redis.

        Args:
            key: The key to set.
            value: The value to set.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.redis_client:
            return False
        try:
            self.redis_client.set(key, value)
            return True
        except Exception as e:
            print(f"Error setting key in Redis: {e}")
            return False

    def get(self, key: str) -> Optional[str]:
        """
        Get a value from Redis by key.

        Args:
            key: The key to get.

        Returns:
            Optional[str]: The value or None if not found or error.
        """
        if not self.redis_client:
            return None
        try:
            return self.redis_client.get(key)
        except Exception as e:
            print(f"Error getting key from Redis: {e}")
            return None

    def delete(self, key: str) -> bool:
        """
        Delete a key from Redis.

        Args:
            key: The key to delete.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.redis_client:
            return False
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Error deleting key from Redis: {e}")
            return False

    def sadd(self, key: str, *values) -> bool:
        """
        Add values to a Redis set.

        Args:
            key: The set key.
            *values: Values to add to the set.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.redis_client:
            return False
        try:
            self.redis_client.sadd(key, *values)
            return True
        except Exception as e:
            print(f"Error adding to set in Redis: {e}")
            return False

    def smembers(self, key: str) -> set:
        """
        Get all members of a Redis set.

        Args:
            key: The set key.

        Returns:
            set: Set of members or empty set if not found or error.
        """
        if not self.redis_client:
            return set()
        try:
            return self.redis_client.smembers(key)
        except Exception as e:
            print(f"Error getting set members from Redis: {e}")
            return set()

    def srem(self, key: str, *values) -> bool:
        """
        Remove values from a Redis set.

        Args:
            key: The set key.
            *values: Values to remove from the set.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.redis_client:
            return False
        try:
            self.redis_client.srem(key, *values)
            return True
        except Exception as e:
            print(f"Error removing from set in Redis: {e}")
            return False
