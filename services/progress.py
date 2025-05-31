from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class ProgressStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class LessonProgress(BaseModel):
    id: Optional[int] = None
    user_id: int
    lesson_id: int
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    time_spent_seconds: int = 0
    last_position_seconds: int = 0  # For video content
    
    class Config:
        orm_mode = True


class ModuleProgress(BaseModel):
    id: Optional[int] = None
    user_id: int
    module_id: int
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    completion_percentage: float = 0.0
    
    class Config:
        orm_mode = True


class CourseProgress(BaseModel):
    id: Optional[int] = None
    user_id: int
    course_id: int
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    completion_percentage: float = 0.0
    
    class Config:
        orm_mode = True


class ProgressService:
    """Service for tracking user progress in the online course platform."""
    
    # Lesson progress methods
    async def update_lesson_progress(self, user_id: int, lesson_id: int, 
                                    status: Optional[ProgressStatus] = None,
                                    time_spent_seconds: Optional[int] = None,
                                    last_position_seconds: Optional[int] = None) -> LessonProgress:
        """Update a user's progress on a specific lesson."""
        # In a real implementation, this would update in a database
        return LessonProgress(user_id=user_id, lesson_id=lesson_id)
    
    async def complete_lesson(self, user_id: int, lesson_id: int) -> LessonProgress:
        """Mark a lesson as completed for a user."""
        # In a real implementation, this would update in a database
        return LessonProgress(
            user_id=user_id, 
            lesson_id=lesson_id,
            status=ProgressStatus.COMPLETED,
            completed_at=datetime.now()
        )
    
    async def get_lesson_progress(self, user_id: int, lesson_id: int) -> Optional[LessonProgress]:
        """Get a user's progress on a specific lesson."""
        # In a real implementation, this would fetch from a database
        return None
    
    # Module progress methods
    async def get_module_progress(self, user_id: int, module_id: int) -> Optional[ModuleProgress]:
        """Get a user's progress on a specific module."""
        # In a real implementation, this would fetch from a database
        return None
    
    async def calculate_module_progress(self, user_id: int, module_id: int) -> ModuleProgress:
        """Calculate and update a user's progress on a module based on lesson completions."""
        # In a real implementation, this would calculate based on lesson progress
        return ModuleProgress(user_id=user_id, module_id=module_id)
    
    # Course progress methods
    async def get_course_progress(self, user_id: int, course_id: int) -> Optional[CourseProgress]:
        """Get a user's progress on a specific course."""
        # In a real implementation, this would fetch from a database
        return None
    
    async def calculate_course_progress(self, user_id: int, course_id: int) -> CourseProgress:
        """Calculate and update a user's progress on a course based on module completions."""
        # In a real implementation, this would calculate based on module progress
        return CourseProgress(user_id=user_id, course_id=course_id)
    
    # Summary methods
    async def get_user_course_progress_summary(self, user_id: int) -> List[CourseProgress]:
        """Get a summary of a user's progress across all enrolled courses."""
        # In a real implementation, this would fetch from a database
        return []