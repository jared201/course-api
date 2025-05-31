from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class CourseLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CourseStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Course(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    instructor_id: int
    level: CourseLevel = CourseLevel.BEGINNER
    price: float = 0.0
    status: CourseStatus = CourseStatus.DRAFT
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    tags: List[str] = []
    thumbnail_url: Optional[str] = None
    
    class Config:
        orm_mode = True


class CourseService:
    """Service for managing courses in the online course platform."""
    
    async def create_course(self, course_data: dict) -> Course:
        """Create a new course."""
        course = Course(**course_data)
        # In a real implementation, this would save to a database
        return course
    
    async def get_course(self, course_id: int) -> Optional[Course]:
        """Get a course by ID."""
        # In a real implementation, this would fetch from a database
        return None
    
    async def update_course(self, course_id: int, course_data: dict) -> Optional[Course]:
        """Update a course's information."""
        # In a real implementation, this would update in a database
        return None
    
    async def delete_course(self, course_id: int) -> bool:
        """Delete a course."""
        # In a real implementation, this would delete from a database
        return True
    
    async def list_courses(self, 
                          skip: int = 0, 
                          limit: int = 100, 
                          filters: Optional[Dict[str, Any]] = None) -> List[Course]:
        """List all courses with pagination and optional filtering."""
        # In a real implementation, this would fetch from a database with filters
        return []
    
    async def publish_course(self, course_id: int) -> Optional[Course]:
        """Change course status to published."""
        # In a real implementation, this would update the course status in a database
        return None
    
    async def archive_course(self, course_id: int) -> Optional[Course]:
        """Change course status to archived."""
        # In a real implementation, this would update the course status in a database
        return None
    
    async def get_instructor_courses(self, instructor_id: int) -> List[Course]:
        """Get all courses by a specific instructor."""
        # In a real implementation, this would fetch from a database
        return []