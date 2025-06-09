from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    FILE = "file"


class Module(BaseModel):
    id: Optional[int] = None
    course_id: int
    title: str
    description: str
    order: int
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        orm_mode = True


class Lesson(BaseModel):
    id: Optional[int] = None
    module_id: int
    title: str
    description: str
    content_type: ContentType
    content: str  # URL for videos/files, text content, or JSON for quizzes/assignments
    duration_minutes: Optional[int] = None  # For video content
    order: int
    is_free_preview: bool = False
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        orm_mode = True


class ContentService:
    """Service for managing course content in the online course platform."""

    # Module methods
    async def create_module(self, module_data: dict) -> Module:
        """Create a new module and save to Redis."""
        from services.redis_manager import RedisManager
        import json
        from datetime import datetime

        module = Module(**module_data)
        if not module.id:
            module.id = int(datetime.now().timestamp())

        # Convert datetime objects to strings for JSON serialization
        module_dict = module.dict()
        module_dict["created_at"] = module_dict["created_at"].isoformat()
        module_dict["updated_at"] = module_dict["updated_at"].isoformat()

        redis_manager = RedisManager()
        module_key = f"module:{module.id}"
        redis_manager.set(module_key, json.dumps(module_dict))

        # Add module ID to course's modules set
        course_modules_key = f"course:{module.course_id}:modules"
        redis_manager.sadd(course_modules_key, module.id)

        return module

    async def get_module(self, module_id: int) -> Optional[Module]:
        """Get a module by ID."""
        # In a real implementation, this would fetch from a database
        from services.redis_manager import RedisManager
        import json
        redis_manager = RedisManager()
        module_key = f"module:{module_id}"
        module_json = redis_manager.get(module_key)
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
    async def get_modules_by_course_id(self, course_id: int) -> List[Module]:
        """Get all modules for a specific course."""
        # In a real implementation, this would fetch from a database
        from services.redis_manager import RedisManager
        redis_manager = RedisManager()
        course_modules_key = f"course:{course_id}:modules"
        module_ids = redis_manager.smembers(course_modules_key)
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

    async def update_module(self, module_id: int, module_data: dict) -> Optional[Module]:
        """Update a module's information."""
        # In a real implementation, this would update in a database
        from services.redis_manager import RedisManager
        import json
        redis_manager = RedisManager()
        module_key = f"module:{module_id}"
        module_json = redis_manager.get(module_key)
        if module_json:
            try:
                module_dict = json.loads(module_json)
                # Update fields
                for key, value in module_data.items():
                    if key in module_dict:
                        module_dict[key] = value
                # Convert datetime objects to strings for JSON serialization
                module_dict["updated_at"] = datetime.now().isoformat()
                redis_manager.set(module_key, json.dumps(module_dict))
                return Module(**module_dict)
            except Exception as e:
                print(f"Error updating module data: {e}")

        return None

    async def delete_module(self, module_id: int) -> bool:
        """Delete a module."""
        # In a real implementation, this would delete from a database
        return True

    async def list_course_modules(self, course_id: int) -> List[Module]:
        """List all modules for a specific course."""
        # In a real implementation, this would fetch from a database
        from services.redis_manager import RedisManager
        redis_manager = RedisManager()
        course_modules_key = f"course:{course_id}:modules"
        module_ids = redis_manager.smembers(course_modules_key)
        if not module_ids:
            return []
        modules = []
        for module_id in module_ids:
            module = await self.get_module(int(module_id))
            if module:
                modules.append(module)
        # Sort modules by order
        modules.sort(key=lambda x: x.order)

        return []

    async def reorder_modules(self, course_id: int, module_order: List[Dict[str, int]]) -> List[Module]:
        """Reorder modules within a course."""
        # In a real implementation, this would update module orders in a database
        return []

    # Lesson methods
    async def create_lesson(self, lesson_data: dict) -> Lesson:
        """Create a new lesson."""
        from services.redis_manager import RedisManager
        import json
        from datetime import datetime

        # Initialize Redis manager
        redis_manager = RedisManager()

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
        redis_manager.set(lesson_key, json.dumps(lesson_dict))

        # Add lesson ID to module's lessons set
        module_lessons_key = f"module:{lesson.module_id}:lessons"
        redis_manager.sadd(module_lessons_key, lesson.id)

        return lesson

    async def get_lesson(self, lesson_id: int) -> Optional[Lesson]:
        """Get a lesson by ID."""
        from services.redis_manager import RedisManager
        import json
        from datetime import datetime

        # Initialize Redis manager
        redis_manager = RedisManager()

        # Get lesson from Redis
        lesson_key = f"lesson:{lesson_id}"
        lesson_json = redis_manager.get(lesson_key)

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

    async def update_lesson(self, lesson_id: int, lesson_data: dict) -> Optional[Lesson]:
        """Update a lesson's information."""
        # In a real implementation, this would update in a database
        return None

    async def delete_lesson(self, lesson_id: int) -> bool:
        """Delete a lesson."""
        # In a real implementation, this would delete from a database
        return True

    async def list_module_lessons(self, module_id: int) -> List[Lesson]:
        """List all lessons for a specific module."""
        from services.redis_manager import RedisManager

        # Initialize Redis manager
        redis_manager = RedisManager()

        # Get lesson IDs from module's lessons set
        module_lessons_key = f"module:{module_id}:lessons"
        lesson_ids = redis_manager.smembers(module_lessons_key)

        if not lesson_ids:
            return []

        # Get lessons by IDs
        lessons = []
        for lesson_id in lesson_ids:
            lesson = await self.get_lesson(int(lesson_id))
            if lesson:
                lessons.append(lesson)

        # Sort lessons by order
        lessons.sort(key=lambda x: x.order)

        return lessons

    async def reorder_lessons(self, module_id: int, lesson_order: List[Dict[str, int]]) -> List[Lesson]:
        """Reorder lessons within a module."""
        # In a real implementation, this would update lesson orders in a database
        return []

    async def get_lessons_by_module_id(self, param: int) -> List[Lesson]:
        """Get all lessons for a specific module."""
        # In a real implementation, this would fetch from a database

        from services.redis_manager import RedisManager
        redis_manager = RedisManager()
        module_lessons_key = f"module:{param}:lessons"
        lesson_ids = redis_manager.smembers(module_lessons_key)
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

