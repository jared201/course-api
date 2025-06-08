import asyncio
from services.course import CourseService
from services.redis_manager import RedisManager
from datetime import datetime

async def test_create_course_and_save_to_redis():
    # Setup Redis manager and CourseService
    redis_manager = RedisManager()
    course_service = CourseService(redis_manager=redis_manager)

    # Define test course data
    course_data = {
        "title": "Test Course",
        "description": "A course for testing Redis save.",
        "instructor_id": 123,
        "level": "beginner",
        "price": 10.0,
        "status": "pending",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "tags": ["test", "redis"],
        "thumbnail_url": None,
        "start_date": None
    }

    # Create course and save to Redis
    course = await course_service.create_course(course_data)
    print(f"Created course: {course}")

    # Retrieve course from Redis
    course_key = f"course:{course.id}"
    saved_course_json = redis_manager.get(course_key)
    print(f"Saved course in Redis: {saved_course_json}")
    assert saved_course_json is not None, "Course was not saved to Redis!"

if __name__ == "__main__":
    asyncio.run(test_create_course_and_save_to_redis())

