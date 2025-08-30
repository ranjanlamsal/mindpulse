import requests
import json
from uuid import uuid4

# API endpoint
SIGNUP_URL = "http://localhost:8000/api/signup/"

# Generate 20 users
users = [
    {"username": f"user_{i}", "email": f"user_{i}@example.com", "password": f"Pass123!_{i}", "role": "employee" if i < 19 else "manager"}
    for i in range(1, 21)
]

# Store user hashes
user_hashes = []

# Signup users
for user in users:
    response = requests.post(SIGNUP_URL, json=user)
    if response.status_code == 200:
        print(f"Created user: {user['username']}")
    else:
        print(f"Failed to create user {user['username']}: {response.text}")

# Login to get user_hash
LOGIN_URL = "http://localhost:8000/api/login/"
for user in users:
    login_data = {"username": user["username"], "password": user["password"]}
    response = requests.post(LOGIN_URL, json=login_data)
    if response.status_code == 200:
        data = response.json()
        user_hashes.append({"username": user["username"], "user_hash": data["user_hash"]})
        print(f"Logged in {user['username']}: {data['user_hash']}")
    else:
        print(f"Failed to login {user['username']}: {response.text}")

# Output user hashes
print("\nUser Hashes:")
print(json.dumps(user_hashes, indent=2))