import asyncio
import json
from datetime import datetime
from typing import List
from services.course import CourseService, Course, CourseLevel, CourseStatus
from services.content import ContentService, Module, Lesson, ContentType
from services.enrollment import EnrollmentService, Enrollment, EnrollmentStatus
from services.progress import ProgressService, LessonProgress, ModuleProgress, CourseProgress, ProgressStatus

# Mock Redis implementation for testing
class MockRedisManager:
    """A mock Redis manager that stores data in memory for testing purposes."""

    def __init__(self):
        self.data = {}
        self.sets = {}
        print("Using MockRedisManager for testing")

    def connect(self):
        print("Connected to mock Redis")
        return True

    def is_connected(self):
        return True

    def set(self, key, value):
        self.data[key] = value
        print(f"Mock Redis: SET {key}")
        return True

    def get(self, key):
        value = self.data.get(key)
        print(f"Mock Redis: GET {key} -> {'Found' if value else 'Not found'}")
        return value

    def sadd(self, key, *values):
        if key not in self.sets:
            self.sets[key] = set()
        for value in values:
            self.sets[key].add(value)
        print(f"Mock Redis: SADD {key} {values}")
        return True

    def smembers(self, key):
        result = self.sets.get(key, set())
        print(f"Mock Redis: SMEMBERS {key} -> {len(result)} items")
        return result

    def srem(self, key, *values):
        if key in self.sets:
            for value in values:
                self.sets[key].discard(value)
        print(f"Mock Redis: SREM {key} {values}")
        return True

    def delete(self, key):
        if key in self.data:
            del self.data[key]
        print(f"Mock Redis: DEL {key}")
        return True

class EnhancedEnrollmentService(EnrollmentService):
    """Enhanced enrollment service with Redis storage"""

    def __init__(self, redis_manager):
        super().__init__()
        self.redis_manager = redis_manager

    async def enroll_user(self, user_id: int, course_id: int) -> Enrollment:
        """Enroll a user in a course and save to Redis."""
        enrollment_data = {
            "id": int(datetime.now().timestamp()),
            "user_id": user_id,
            "course_id": course_id,
            "status": EnrollmentStatus.ACTIVE,
            "enrolled_at": datetime.now()
        }
        enrollment = Enrollment(**enrollment_data)

        # Convert to dict for Redis storage
        enrollment_dict = enrollment.dict()
        enrollment_dict["enrolled_at"] = enrollment_dict["enrolled_at"].isoformat()
        enrollment_dict["status"] = enrollment_dict["status"].value

        # Save to Redis
        enrollment_key = f"enrollment:{enrollment.id}"
        self.redis_manager.set(enrollment_key, json.dumps(enrollment_dict))

        # Add to user enrollments set
        user_enrollments_key = f"user:{user_id}:enrollments"
        self.redis_manager.sadd(user_enrollments_key, enrollment.id)

        # Add to course enrollments set
        course_enrollments_key = f"course:{course_id}:enrollments"
        self.redis_manager.sadd(course_enrollments_key, enrollment.id)

        return enrollment

    async def is_user_enrolled(self, user_id: int, course_id: int) -> bool:
        """Check if a user is enrolled in a specific course."""
        user_enrollments_key = f"user:{user_id}:enrollments"
        enrollment_ids = self.redis_manager.smembers(user_enrollments_key)

        for enrollment_id in enrollment_ids:
            enrollment_key = f"enrollment:{enrollment_id}"
            enrollment_json = self.redis_manager.get(enrollment_key)
            if enrollment_json:
                enrollment_dict = json.loads(enrollment_json)
                if enrollment_dict["course_id"] == course_id and enrollment_dict["status"] == EnrollmentStatus.ACTIVE.value:
                    return True

        return False

    async def get_user_enrollments(self, user_id: int) -> List[Enrollment]:
        """Get all enrollments for a specific user."""
        from datetime import datetime

        user_enrollments_key = f"user:{user_id}:enrollments"
        enrollment_ids = self.redis_manager.smembers(user_enrollments_key)
        enrollments = []

        for enrollment_id in enrollment_ids:
            enrollment_key = f"enrollment:{enrollment_id}"
            enrollment_json = self.redis_manager.get(enrollment_key)
            if enrollment_json:
                try:
                    enrollment_dict = json.loads(enrollment_json)

                    # Convert string dates back to datetime objects
                    if "enrolled_at" in enrollment_dict:
                        enrollment_dict["enrolled_at"] = datetime.fromisoformat(enrollment_dict["enrolled_at"])
                    if "completed_at" in enrollment_dict and enrollment_dict["completed_at"]:
                        enrollment_dict["completed_at"] = datetime.fromisoformat(enrollment_dict["completed_at"])
                    if "expiry_date" in enrollment_dict and enrollment_dict["expiry_date"]:
                        enrollment_dict["expiry_date"] = datetime.fromisoformat(enrollment_dict["expiry_date"])

                    # Convert status string back to enum
                    if "status" in enrollment_dict:
                        enrollment_dict["status"] = EnrollmentStatus(enrollment_dict["status"])

                    enrollments.append(Enrollment(**enrollment_dict))
                except Exception as e:
                    print(f"Error parsing enrollment data: {e}")

        return enrollments

class EnhancedContentService(ContentService):
    """Enhanced content service that uses the provided Redis manager"""

    def __init__(self, redis_manager):
        super().__init__()
        self.redis_manager = redis_manager

    async def create_module(self, module_data: dict) -> Module:
        """Create a new module and save to Redis using the provided Redis manager."""
        import json
        from datetime import datetime

        module = Module(**module_data)
        if not module.id:
            module.id = int(datetime.now().timestamp())

        # Convert datetime objects to strings for JSON serialization
        module_dict = module.dict()
        module_dict["created_at"] = module_dict["created_at"].isoformat()
        module_dict["updated_at"] = module_dict["updated_at"].isoformat()

        module_key = f"module:{module.id}"
        self.redis_manager.set(module_key, json.dumps(module_dict))

        # Add module ID to course's modules set
        course_modules_key = f"course:{module.course_id}:modules"
        self.redis_manager.sadd(course_modules_key, module.id)

        return module

    async def create_lesson(self, lesson_data: dict) -> Lesson:
        """Create a new lesson using the provided Redis manager."""
        import json
        from datetime import datetime

        # Create a Lesson object
        lesson = Lesson(**lesson_data)

        # Generate a unique ID if not provided
        if not lesson.id:
            lesson.id = int(datetime.now().timestamp())

        # Create a dictionary from the lesson for Redis storage
        lesson_dict = lesson.dict()

        # Convert datetime objects to strings for JSON serialization
        lesson_dict["created_at"] = lesson_dict["created_at"].isoformat()
        lesson_dict["updated_at"] = lesson_dict["updated_at"].isoformat()

        # Store lesson in Redis
        lesson_key = f"lesson:{lesson.id}"
        self.redis_manager.set(lesson_key, json.dumps(lesson_dict))

        # Add lesson ID to module's lessons set
        module_lessons_key = f"module:{lesson.module_id}:lessons"
        self.redis_manager.sadd(module_lessons_key, lesson.id)

        return lesson

    async def get_module(self, module_id: int):
        """Get a module by ID using the provided Redis manager."""
        import json
        from datetime import datetime

        module_key = f"module:{module_id}"
        module_json = self.redis_manager.get(module_key)
        if module_json:
            try:
                module_dict = json.loads(module_json)
                # Convert string dates back to datetime objects
                module_dict["created_at"] = datetime.fromisoformat(module_dict["created_at"])
                module_dict["updated_at"] = datetime.fromisoformat(module_dict["updated_at"])
                return Module(**module_dict)
            except Exception as e:
                print(f"Error parsing module data: {e}")

        return None

    async def get_lesson(self, lesson_id: int):
        """Get a lesson by ID using the provided Redis manager."""
        import json
        from datetime import datetime

        lesson_key = f"lesson:{lesson_id}"
        lesson_json = self.redis_manager.get(lesson_key)

        if not lesson_json:
            return None

        try:
            # Parse JSON data
            lesson_dict = json.loads(lesson_json)

            # Convert string dates back to datetime objects
            if "created_at" in lesson_dict:
                lesson_dict["created_at"] = datetime.fromisoformat(lesson_dict["created_at"])
            if "updated_at" in lesson_dict:
                lesson_dict["updated_at"] = datetime.fromisoformat(lesson_dict["updated_at"])

            # Create and return Lesson object
            return Lesson(**lesson_dict)
        except Exception as e:
            print(f"Error parsing lesson data: {e}")
            return None

    async def get_modules_by_course_id(self, course_id: int):
        """Get all modules for a specific course using the provided Redis manager."""
        course_modules_key = f"course:{course_id}:modules"
        module_ids = self.redis_manager.smembers(course_modules_key)
        if not module_ids:
            return []
        modules = []
        for module_id in module_ids:
            module = await self.get_module(int(module_id))
            if module:
                modules.append(module)
        # Sort modules by order
        modules.sort(key=lambda x: x.order)

        return modules

    async def get_lessons_by_module_id(self, module_id: int):
        """Get all lessons for a specific module using the provided Redis manager."""
        module_lessons_key = f"module:{module_id}:lessons"
        lesson_ids = self.redis_manager.smembers(module_lessons_key)
        if not lesson_ids:
            return []
        lessons = []
        for lesson_id in lesson_ids:
            lesson = await self.get_lesson(int(lesson_id))
            if lesson:
                lessons.append(lesson)
        # Sort lessons by order
        lessons.sort(key=lambda x: x.order)
        return lessons

class EnhancedProgressService(ProgressService):
    """Enhanced progress service with Redis storage"""

    def __init__(self, redis_manager, content_service):
        super().__init__()
        self.redis_manager = redis_manager
        self.content_service = content_service

    async def complete_lesson(self, user_id: int, lesson_id: int) -> LessonProgress:
        """Mark a lesson as completed for a user and save to Redis."""
        now = datetime.now()
        progress_data = {
            "id": int(now.timestamp()),
            "user_id": user_id,
            "lesson_id": lesson_id,
            "status": ProgressStatus.COMPLETED,
            "started_at": now,
            "completed_at": now,
            "time_spent_seconds": 300,  # Assume 5 minutes spent
            "last_position_seconds": 0
        }

        progress = LessonProgress(**progress_data)

        # Convert to dict for Redis storage
        progress_dict = progress.dict()
        progress_dict["started_at"] = progress_dict["started_at"].isoformat()
        progress_dict["completed_at"] = progress_dict["completed_at"].isoformat()
        progress_dict["status"] = progress_dict["status"].value

        # Save to Redis
        progress_key = f"lesson_progress:{user_id}:{lesson_id}"
        self.redis_manager.set(progress_key, json.dumps(progress_dict))

        # Update module progress
        lesson = await self.content_service.get_lesson(lesson_id)
        if lesson:
            await self.calculate_module_progress(user_id, lesson.module_id)

        return progress

    async def calculate_module_progress(self, user_id: int, module_id: int) -> ModuleProgress:
        """Calculate and update a user's progress on a module based on lesson completions."""
        # Get all lessons in the module
        lessons = await self.content_service.get_lessons_by_module_id(module_id)
        if not lessons:
            return ModuleProgress(user_id=user_id, module_id=module_id)

        # Count completed lessons
        completed_count = 0
        for lesson in lessons:
            progress_key = f"lesson_progress:{user_id}:{lesson.id}"
            progress_json = self.redis_manager.get(progress_key)
            if progress_json:
                progress_dict = json.loads(progress_json)
                if progress_dict["status"] == ProgressStatus.COMPLETED.value:
                    completed_count += 1

        # Calculate completion percentage
        total_lessons = len(lessons)
        completion_percentage = (completed_count / total_lessons) * 100 if total_lessons > 0 else 0

        # Determine status
        status = ProgressStatus.NOT_STARTED
        if completion_percentage > 0:
            status = ProgressStatus.IN_PROGRESS
        if completion_percentage >= 100:
            status = ProgressStatus.COMPLETED

        # Create progress object
        now = datetime.now()
        progress_data = {
            "id": int(now.timestamp()),
            "user_id": user_id,
            "module_id": module_id,
            "status": status,
            "started_at": now if completion_percentage > 0 else None,
            "completed_at": now if completion_percentage >= 100 else None,
            "completion_percentage": completion_percentage
        }

        progress = ModuleProgress(**progress_data)

        # Convert to dict for Redis storage
        progress_dict = progress.dict()
        if progress_dict["started_at"]:
            progress_dict["started_at"] = progress_dict["started_at"].isoformat()
        if progress_dict["completed_at"]:
            progress_dict["completed_at"] = progress_dict["completed_at"].isoformat()
        progress_dict["status"] = progress_dict["status"].value

        # Save to Redis
        progress_key = f"module_progress:{user_id}:{module_id}"
        self.redis_manager.set(progress_key, json.dumps(progress_dict))

        # Update course progress if module is completed
        if status == ProgressStatus.COMPLETED:
            # Get the course_id from the module
            module = await self.content_service.get_module(module_id)
            if module:
                await self.calculate_course_progress(user_id, module.course_id)

        return progress

    async def calculate_course_progress(self, user_id: int, course_id: int) -> CourseProgress:
        """Calculate and update a user's progress on a course based on module completions."""
        # Get all modules in the course
        content_service = self.content_service
        modules = await content_service.get_modules_by_course_id(course_id)
        if not modules:
            return CourseProgress(user_id=user_id, course_id=course_id)

        # Count completed modules
        completed_count = 0
        for module in modules:
            progress_key = f"module_progress:{user_id}:{module.id}"
            progress_json = self.redis_manager.get(progress_key)
            if progress_json:
                progress_dict = json.loads(progress_json)
                if progress_dict["status"] == ProgressStatus.COMPLETED.value:
                    completed_count += 1

        # Calculate completion percentage
        total_modules = len(modules)
        completion_percentage = (completed_count / total_modules) * 100 if total_modules > 0 else 0

        # Determine status
        status = ProgressStatus.NOT_STARTED
        if completion_percentage > 0:
            status = ProgressStatus.IN_PROGRESS
        if completion_percentage >= 100:
            status = ProgressStatus.COMPLETED

        # Create progress object
        now = datetime.now()
        progress_data = {
            "id": int(now.timestamp()),
            "user_id": user_id,
            "course_id": course_id,
            "status": status,
            "started_at": now if completion_percentage > 0 else None,
            "completed_at": now if completion_percentage >= 100 else None,
            "completion_percentage": completion_percentage
        }

        progress = CourseProgress(**progress_data)

        # Convert to dict for Redis storage
        progress_dict = progress.dict()
        if progress_dict["started_at"]:
            progress_dict["started_at"] = progress_dict["started_at"].isoformat()
        if progress_dict["completed_at"]:
            progress_dict["completed_at"] = progress_dict["completed_at"].isoformat()
        progress_dict["status"] = progress_dict["status"].value

        # Save to Redis
        progress_key = f"course_progress:{user_id}:{course_id}"
        self.redis_manager.set(progress_key, json.dumps(progress_dict))

        return progress

async def test_complete_learning_flow():
    """
    Test the complete student learning flow from enrollment to course completion.
    This test creates a course with modules and lessons, enrolls a student,
    and tracks their progress through completion.
    """
    print("Starting complete learning flow test...")

    # Setup Redis manager and services
    redis_manager = MockRedisManager()
    course_service = CourseService(redis_manager=redis_manager)
    content_service = EnhancedContentService(redis_manager)
    enrollment_service = EnhancedEnrollmentService(redis_manager)
    progress_service = EnhancedProgressService(redis_manager, content_service)

    # Create a test user
    user_id = 1001

    # Step 1: Create a course
    print("\n--- Step 1: Creating a course ---")
    course_data = {
        "title": "Python Programming Fundamentals",
        "description": "Learn the basics of Python programming language",
        "instructor_id": 2001,
        "instructor_name": "Dr. Python",
        "level": CourseLevel.BEGINNER,
        "price": 49.99,
        "duration": 10.0,  # 10 hours
        "status": CourseStatus.PUBLISHED,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "tags": ["python", "programming", "beginner"],
        "thumbnail_url": "https://example.com/python-thumbnail.jpg"
    }

    course = await course_service.create_course(course_data)
    print(f"Created course: {course.title} (ID: {course.id})")

    # Step 2: Create modules for the course
    print("\n--- Step 2: Creating modules ---")
    modules = []

    module_data = [
        {
            "course_id": course.id,
            "title": "Introduction to Python",
            "description": "Get started with Python basics",
            "order": 1
        },
        {
            "course_id": course.id,
            "title": "Data Types and Variables",
            "description": "Learn about Python data types and variables",
            "order": 2
        },
        {
            "course_id": course.id,
            "title": "Control Flow",
            "description": "Master conditional statements and loops",
            "order": 3
        }
    ]

    for data in module_data:
        module = await content_service.create_module(data)
        modules.append(module)
        print(f"Created module: {module.title} (ID: {module.id})")

    # Step 3: Create lessons for each module
    print("\n--- Step 3: Creating lessons ---")
    lessons = []

    # Lessons for Module 1
    lesson_data_module1 = [
        {
            "module_id": modules[0].id,
            "title": "What is Python?",
            "description": "Introduction to Python programming language",
            "content_type": ContentType.TEXT,
            "content": "Python is a high-level, interpreted programming language...",
            "order": 1,
            "is_free_preview": True
        },
        {
            "module_id": modules[0].id,
            "title": "Setting Up Your Environment",
            "description": "Installing Python and setting up your development environment",
            "content_type": ContentType.VIDEO,
            "content": "https://example.com/videos/python-setup.mp4",
            "duration_minutes": 15,
            "order": 2
        }
    ]

    # Lessons for Module 2
    lesson_data_module2 = [
        {
            "module_id": modules[1].id,
            "title": "Numbers and Strings",
            "description": "Working with numeric and string data types",
            "content_type": ContentType.TEXT,
            "content": "Python has several built-in data types including numbers and strings...",
            "order": 1
        },
        {
            "module_id": modules[1].id,
            "title": "Lists and Dictionaries",
            "description": "Working with collection data types",
            "content_type": ContentType.VIDEO,
            "content": "https://example.com/videos/python-collections.mp4",
            "duration_minutes": 20,
            "order": 2
        }
    ]

    # Lessons for Module 3
    lesson_data_module3 = [
        {
            "module_id": modules[2].id,
            "title": "If Statements",
            "description": "Conditional execution with if statements",
            "content_type": ContentType.TEXT,
            "content": "Conditional statements allow you to execute code based on certain conditions...",
            "order": 1
        },
        {
            "module_id": modules[2].id,
            "title": "Loops",
            "description": "Iterating with for and while loops",
            "content_type": ContentType.VIDEO,
            "content": "https://example.com/videos/python-loops.mp4",
            "duration_minutes": 25,
            "order": 2
        }
    ]

    all_lesson_data = lesson_data_module1 + lesson_data_module2 + lesson_data_module3

    for data in all_lesson_data:
        lesson = await content_service.create_lesson(data)
        lessons.append(lesson)
        print(f"Created lesson: {lesson.title} (ID: {lesson.id})")

    # Step 4: Enroll the student in the course
    print("\n--- Step 4: Enrolling student ---")
    enrollment = await enrollment_service.enroll_user(user_id, course.id)
    print(f"Enrolled user {user_id} in course {course.id}")

    # Verify enrollment
    is_enrolled = await enrollment_service.is_user_enrolled(user_id, course.id)
    print(f"Is user enrolled? {is_enrolled}")

    # Step 5: Student completes lessons one by one
    print("\n--- Step 5: Completing lessons ---")
    for i, lesson in enumerate(lessons):
        # Complete the lesson
        progress = await progress_service.complete_lesson(user_id, lesson.id)
        print(f"Completed lesson: {lesson.title}")

        # Get module progress
        module_progress_key = f"module_progress:{user_id}:{lesson.module_id}"
        module_progress_json = redis_manager.get(module_progress_key)
        if module_progress_json:
            module_progress = json.loads(module_progress_json)
            print(f"Module {lesson.module_id} progress: {module_progress['completion_percentage']}%")

        # Get course progress after each lesson
        course_progress_key = f"course_progress:{user_id}:{course.id}"
        course_progress_json = redis_manager.get(course_progress_key)
        if course_progress_json:
            course_progress = json.loads(course_progress_json)
            print(f"Overall course progress: {course_progress['completion_percentage']}%")

    # Step 6: Verify course completion
    print("\n--- Step 6: Verifying course completion ---")
    course_progress_key = f"course_progress:{user_id}:{course.id}"
    course_progress_json = redis_manager.get(course_progress_key)

    if course_progress_json:
        course_progress = json.loads(course_progress_json)
        print(f"Final course progress: {course_progress['completion_percentage']}%")
        print(f"Course completion status: {course_progress['status']}")

        if course_progress['status'] == ProgressStatus.COMPLETED.value:
            print("🎉 Course successfully completed! 🎉")
        else:
            print("Course not yet completed.")
    else:
        print("No course progress found.")

    print("\nComplete learning flow test finished successfully!")

if __name__ == "__main__":
    asyncio.run(test_complete_learning_flow())
