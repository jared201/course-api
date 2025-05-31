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
        """Create a new module."""
        module = Module(**module_data)
        # In a real implementation, this would save to a database
        return module
    
    async def get_module(self, module_id: int) -> Optional[Module]:
        """Get a module by ID."""
        # In a real implementation, this would fetch from a database
        return None
    
    async def update_module(self, module_id: int, module_data: dict) -> Optional[Module]:
        """Update a module's information."""
        # In a real implementation, this would update in a database
        return None
    
    async def delete_module(self, module_id: int) -> bool:
        """Delete a module."""
        # In a real implementation, this would delete from a database
        return True
    
    async def list_course_modules(self, course_id: int) -> List[Module]:
        """List all modules for a specific course."""
        # In a real implementation, this would fetch from a database
        return []
    
    async def reorder_modules(self, course_id: int, module_order: List[Dict[str, int]]) -> List[Module]:
        """Reorder modules within a course."""
        # In a real implementation, this would update module orders in a database
        return []
    
    # Lesson methods
    async def create_lesson(self, lesson_data: dict) -> Lesson:
        """Create a new lesson."""
        lesson = Lesson(**lesson_data)
        # In a real implementation, this would save to a database
        return lesson
    
    async def get_lesson(self, lesson_id: int) -> Optional[Lesson]:
        """Get a lesson by ID."""
        # In a real implementation, this would fetch from a database
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
        # In a real implementation, this would fetch from a database
        return []
    
    async def reorder_lessons(self, module_id: int, lesson_order: List[Dict[str, int]]) -> List[Lesson]:
        """Reorder lessons within a module."""
        # In a real implementation, this would update lesson orders in a database
        return []