from services.user import User, UserRole, DateTimeEncoder
from datetime import datetime
import json

# Create a user with datetime fields
user = User(
    id=1,
    username="testuser",
    email="test@example.com",
    full_name="Test User",
    role=UserRole.STUDENT,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

# Try to serialize to JSON with and without the custom encoder
try:
    # This should fail without the custom encoder
    standard_json = json.dumps(user.dict())
    print("Standard JSON serialization succeeded (unexpected):", standard_json[:100])
except Exception as e:
    print(f"Standard JSON serialization failed (expected): {e}")

try:
    # This should succeed with our custom encoder
    custom_json = json.dumps(user.dict(), cls=DateTimeEncoder)
    print("Custom JSON serialization succeeded:", custom_json[:100])
except Exception as e:
    print(f"Custom JSON serialization failed (unexpected): {e}")

print("\nTest completed. If you see 'Custom JSON serialization succeeded' above, the fix is working.")