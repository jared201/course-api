import requests
import json

"""
Test script for the Redis integration endpoint.

Prerequisites:
1. Make sure Redis server is running
2. Make sure the API server is running (uvicorn main:app --reload)
3. Create an admin account using create_admin_account.py:
   python create_admin_account.py
"""

# Base URL for the API
base_url = "http://localhost:8000"

# Endpoint to test
endpoint = "/admin/courses/move-to-redis"

# First, we need to get a token by logging in
def get_token():
    login_url = f"{base_url}/token"
    login_data = {
        "username": "admin",  # This uses the admin account created by create_admin_account.py
        "password": "admin"   # Password for the admin account
    }

    response = requests.post(login_url, data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data["access_token"]
    else:
        print(f"Failed to login: {response.status_code} - {response.text}")
        print("Make sure you've created an admin account using create_admin_account.py")
        return None

# Call the endpoint to move courses to Redis
def move_courses_to_redis(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(f"{base_url}{endpoint}", headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    return response.status_code == 200

if __name__ == "__main__":
    print("Getting authentication token...")
    token = get_token()

    if token:
        print("Token obtained successfully.")
        print("Calling endpoint to move courses to Redis...")
        success = move_courses_to_redis(token)

        if success:
            print("Successfully moved course data to Redis!")
        else:
            print("Failed to move course data to Redis.")
    else:
        print("Failed to get authentication token. Make sure the API is running and credentials are correct.")
