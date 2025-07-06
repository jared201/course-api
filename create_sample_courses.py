import asyncio
import json
from datetime import datetime, timedelta
from services.redis_manager import RedisManager
from services.course import CourseService, Course, CourseLevel, CourseStatus
from services.content import ContentService, Module, Lesson, ContentType

async def create_sample_courses():
    """Create 10 sample courses with 3 modules each and 3 lessons per module."""
    print("Creating sample courses...")

    # Initialize services
    redis_manager = RedisManager()
    course_service = CourseService(redis_manager=redis_manager)
    content_service = ContentService()

    # Sample course topics
    course_topics = [
        "Python Programming",
        "Web Development",
        "Data Science",
        "Machine Learning",
        "Mobile App Development",
        "Cloud Computing",
        "DevOps",
        "Cybersecurity",
        "Blockchain",
        "Artificial Intelligence"
    ]

    # Sample instructor IDs (in a real app, these would be actual user IDs)
    instructor_ids = [1, 2, 3, 4, 5]

    # Lists to store created IDs for verification
    created_course_ids = []
    created_module_ids = []
    created_lesson_ids = []

    # Create 10 sample courses
    for i in range(10):
        # Create course data
        course_data = {
            "id": 1000 + i,
            "title": f"{course_topics[i]} Fundamentals",
            "description": f"Learn the fundamentals of {course_topics[i]} in this comprehensive course.",
            "instructor_id": instructor_ids[i % len(instructor_ids)],
            "instructor_name": f"Instructor {instructor_ids[i % len(instructor_ids)]}",
            "level": CourseLevel.BEGINNER,
            "price": 49.99,
            "duration": 12.0,  # hours
            "status": CourseStatus.PUBLISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "start_date": datetime.now() + timedelta(days=7),
            "tags": [course_topics[i].lower(), "beginner", "online"],
            "thumbnail_url": f"https://example.com/thumbnails/{course_topics[i].lower().replace(' ', '_')}.jpg"
        }

        # Create the course
        course = await course_service.create_course(course_data)
        created_course_ids.append(course.id)
        print(f"Created course: {course.title} (ID: {course.id})")

        # Create 3 modules for each course
        for j in range(3):
            module_data = {
                "id": 10000 + (i * 3) + j,
                "course_id": course.id,
                "title": f"Module {j+1}: {['Introduction', 'Core Concepts', 'Advanced Topics'][j]} of {course_topics[i]}",
                "description": f"This module covers {['the basics', 'essential concepts', 'advanced topics'][j]} of {course_topics[i]}.",
                "order": j + 1
            }

            # Create the module
            module = await content_service.create_module(module_data)
            created_module_ids.append(module.id)
            print(f"  Created module: {module.title} (ID: {module.id})")

            # Create 3 lessons for each module
            for k in range(3):
                lesson_data = {
                    "id": 100000 + (i * 9) + (j * 3) + k,
                    "module_id": module.id,
                    "title": f"Lesson {k+1}: {['Getting Started', 'Key Principles', 'Practical Application'][k]}",
                    "description": f"Learn about {['the fundamentals', 'important concepts', 'practical applications'][k]} in this lesson.",
                    "content_type": ContentType.TEXT,
                    "content": f"This is the content for lesson {k+1} of module {j+1} in the {course_topics[i]} course.",
                    "duration_minutes": 30,
                    "order": k + 1,
                    "is_free_preview": k == 0  # First lesson is free preview
                }

                # Create the lesson
                lesson = await content_service.create_lesson(lesson_data)
                created_lesson_ids.append(lesson.id)
                print(f"    Created lesson: {lesson.title} (ID: {lesson.id})")

    # Verify that courses, modules, and lessons were created in Redis
    print("\nVerifying courses in Redis...")
    all_courses = redis_manager.smembers("all_courses")
    print(f"Found {len(all_courses)} courses in Redis all_courses set")

    for course_id in created_course_ids:
        course_key = f"course:{course_id}"
        course_data = redis_manager.get(course_key)
        if course_data:
            print(f"✓ Course {course_id} found in Redis")
        else:
            print(f"✗ Course {course_id} NOT found in Redis")

    print("\nVerifying modules in Redis...")
    for module_id in created_module_ids:
        module_key = f"module:{module_id}"
        module_data = redis_manager.get(module_key)
        if module_data:
            print(f"✓ Module {module_id} found in Redis")
        else:
            print(f"✗ Module {module_id} NOT found in Redis")

    print("\nVerifying lessons in Redis...")
    for lesson_id in created_lesson_ids:
        lesson_key = f"lesson:{lesson_id}"
        lesson_data = redis_manager.get(lesson_key)
        if lesson_data:
            print(f"✓ Lesson {lesson_id} found in Redis")
        else:
            print(f"✗ Lesson {lesson_id} NOT found in Redis")

    print("\nSample courses created successfully!")
    print(f"Created {len(created_course_ids)} courses, {len(created_module_ids)} modules, and {len(created_lesson_ids)} lessons")

async def verify_enrollment_possible():
    """Verify that students can enroll in the created courses."""
    print("\nVerifying that courses can be enrolled...")

    # Initialize Redis manager
    redis_manager = RedisManager()

    # Get all courses
    all_courses = redis_manager.smembers("all_courses")
    if not all_courses:
        print("No courses found in Redis!")
        return

    # Check if courses are in the correct format for enrollment
    course_id = next(iter(all_courses))
    course_key = f"course:{course_id}"
    course_data = redis_manager.get(course_key)

    if course_data:
        try:
            course_dict = json.loads(course_data)
            print(f"Course {course_id} is available for enrollment:")
            print(f"  Title: {course_dict.get('title')}")
            print(f"  Status: {course_dict.get('status')}")

            # Check if course has modules
            course_modules_key = f"course:{course_id}:modules"
            module_ids = redis_manager.smembers(course_modules_key)
            print(f"  Modules: {len(module_ids)}")

            if module_ids:
                module_id = next(iter(module_ids))
                module_key = f"module:{module_id}"
                module_data = redis_manager.get(module_key)

                if module_data:
                    module_dict = json.loads(module_data)
                    print(f"  Module {module_id} is available:")
                    print(f"    Title: {module_dict.get('title')}")

                    # Check if module has lessons
                    module_lessons_key = f"module:{module_id}:lessons"
                    lesson_ids = redis_manager.smembers(module_lessons_key)
                    print(f"    Lessons: {len(lesson_ids)}")

                    if lesson_ids:
                        print("✓ Courses are properly structured for enrollment and completion")
                    else:
                        print("✗ Module has no lessons")
                else:
                    print("✗ Module data not found")
            else:
                print("✗ Course has no modules")
        except json.JSONDecodeError:
            print(f"✗ Course {course_id} data is not valid JSON")
    else:
        print(f"✗ Course {course_id} data not found")

if __name__ == "__main__":
    asyncio.run(create_sample_courses())
    asyncio.run(verify_enrollment_possible())
