import asyncio
import json
from services.content import ContentService
from services.redis_manager import RedisManager

async def test_module_saved_in_redis():
    redis_manager = RedisManager()
    content_service = ContentService()

    # Create a test module
    module_data = {
        "course_id": 123,
        "title": "Test Module",
        "description": "A module for testing",
        "order": 1
    }
    module = await content_service.create_module(module_data)
    module_id = module.id

    # Check if module exists in Redis
    module_key = f"module:{module_id}"
    module_json = redis_manager.get(module_key)
    assert module_json is not None, "Module not found in Redis"

    module_from_redis = json.loads(module_json)
    assert module_from_redis["title"] == "Test Module"
    assert module_from_redis["course_id"] == 123

    # Cleanup
    redis_manager.delete(module_key)
    print("Test passed: Module is saved in Redis.")

if __name__ == "__main__":
    asyncio.run(test_module_saved_in_redis())