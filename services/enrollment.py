from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class EnrollmentStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"
    EXPIRED = "expired"


class Enrollment(BaseModel):
    id: Optional[int] = None
    user_id: int
    course_id: int
    status: EnrollmentStatus = EnrollmentStatus.ACTIVE
    enrolled_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class EnrollmentService:
    """Service for managing course enrollments in the online course platform."""
    
    async def enroll_user(self, user_id: int, course_id: int) -> Enrollment:
        """Enroll a user in a course."""
        enrollment_data = {
            "user_id": user_id,
            "course_id": course_id,
        }
        enrollment = Enrollment(**enrollment_data)
        # In a real implementation, this would save to a database
        return enrollment
    
    async def get_enrollment(self, enrollment_id: int) -> Optional[Enrollment]:
        """Get an enrollment by ID."""
        # In a real implementation, this would fetch from a database
        return None
    
    async def update_enrollment_status(self, enrollment_id: int, status: EnrollmentStatus) -> Optional[Enrollment]:
        """Update an enrollment's status."""
        # In a real implementation, this would update in a database
        return None
    
    async def complete_enrollment(self, enrollment_id: int) -> Optional[Enrollment]:
        """Mark an enrollment as completed."""
        # In a real implementation, this would update in a database
        return None
    
    async def drop_enrollment(self, enrollment_id: int) -> Optional[Enrollment]:
        """Mark an enrollment as dropped."""
        # In a real implementation, this would update in a database
        return None
    
    async def get_user_enrollments(self, user_id: int) -> List[Enrollment]:
        """Get all enrollments for a specific user."""
        # In a real implementation, this would fetch from a database
        return []
    
    async def get_course_enrollments(self, course_id: int) -> List[Enrollment]:
        """Get all enrollments for a specific course."""
        # In a real implementation, this would fetch from a database
        return []
    
    async def is_user_enrolled(self, user_id: int, course_id: int) -> bool:
        """Check if a user is enrolled in a specific course."""
        # In a real implementation, this would check in a database
        return False