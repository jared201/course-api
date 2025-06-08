from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import json


class CourseLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CourseStatus(str, Enum):
    PENDING = "pending"
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
    status: CourseStatus = CourseStatus.PENDING
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    start_date: Optional[datetime] = None
    tags: List[str] = []
    thumbnail_url: Optional[str] = None

    class Config:
        orm_mode = True


class CourseService:
    """Service for managing courses in the online course platform."""

    def __init__(self, featured_courses=None, trending_courses=None, redis_manager=None):
        self.featured_courses = featured_courses or []
        self.trending_courses = trending_courses or []
        self.redis_manager = redis_manager

    async def create_course(self, course_data: dict) -> Course:
        """Create a new course."""
        # Always ensure Redis is connected before saving
        if self.redis_manager:
            try:
                if not self.redis_manager.is_connected():
                    self.redis_manager.connect()
                # Generate a unique ID if not provided
                if course_data.get("id") is None:
                    course_data["id"] = int(datetime.now().timestamp())
                # Convert datetime objects to strings for JSON serialization
                course_dict = course_data
                course_dict["created_at"] = course_dict["created_at"].isoformat()
                course_dict["updated_at"] = course_dict["updated_at"].isoformat()
                if course_dict["start_date"]:
                    course_dict["start_date"] = course_dict["start_date"].isoformat()
                # Store individual course
                course_key = f"course:{course_dict['id']}"
                result = self.redis_manager.set(course_key, json.dumps(course_dict))
                if not result:
                    print(f"Failed to save course {course_dict['id']} to Redis!")
                else:
                    print(f"Course {course_dict['id']} saved to Redis")
                # Add to all courses set
                self.redis_manager.sadd("all_courses", course_dict["id"])
            except Exception as e:
                print(f"Error saving course to Redis: {e}")
        else:
            print("Redis manager not set on CourseService!")
        return course_data

    async def get_course(self, course_id: int) -> Optional[Course]:
        """Get a course by ID."""
        # If Redis manager is available, try to fetch from Redis
        if self.redis_manager and self.redis_manager.is_connected():
            course_key = f"course:{course_id}"
            course_data = self.redis_manager.get(course_key)
            if course_data:
                try:
                    # Parse the JSON data
                    course_dict = json.loads(course_data)
                    # Convert ISO format strings back to datetime objects
                    if "created_at" in course_dict:
                        course_dict["created_at"] = datetime.fromisoformat(course_dict["created_at"])
                    if "updated_at" in course_dict:
                        course_dict["updated_at"] = datetime.fromisoformat(course_dict["updated_at"])
                    if "start_date" in course_dict and course_dict["start_date"]:
                        course_dict["start_date"] = datetime.fromisoformat(course_dict["start_date"])
                    return Course(**course_dict)
                except Exception as e:
                    print(f"Error parsing course data from Redis: {e}")

        # Fallback to searching in instance variables
        for course in self.featured_courses + self.trending_courses:
            if course.get("id") == course_id:
                return Course(**course)

        return None

    async def update_course(self, course_id: int, course_data: dict) -> Optional[Course]:
        """Update a course's information."""
        # Get the existing course
        existing_course = await self.get_course(course_id)
        if not existing_course:
            return None

        # Update the course with new data
        existing_dict = existing_course.dict()
        for key, value in course_data.items():
            if key in existing_dict:
                # Handle enum conversions
                if key == "level" and isinstance(value, str):
                    try:
                        existing_dict[key] = CourseLevel(value.lower())
                    except Exception as e:
                        print(f"Error converting level to Enum: {e}")
                elif key == "status" and isinstance(value, str):
                    try:
                        existing_dict[key] = CourseStatus(value.lower())
                    except Exception as e:
                        print(f"Error converting status to Enum: {e}")
                else:
                    existing_dict[key] = value

        # Update the updated_at timestamp
        existing_dict["updated_at"] = datetime.now()

        # Create updated course object
        updated_course = Course(**existing_dict)

        # Save to Redis
        if self.redis_manager and self.redis_manager.is_connected():
            try:
                # Convert datetime objects to strings for JSON serialization
                course_dict = updated_course.dict()
                course_dict["created_at"] = course_dict["created_at"].isoformat()
                course_dict["updated_at"] = course_dict["updated_at"].isoformat()
                if course_dict["start_date"]:
                    course_dict["start_date"] = course_dict["start_date"].isoformat()

                # Store updated course
                course_key = f"course:{updated_course.id}"
                result = self.redis_manager.set(course_key, json.dumps(course_dict))
                if not result:
                    print(f"Failed to update course {updated_course.id} in Redis!")
                else:
                    print(f"Course {updated_course.id} updated in Redis")
            except Exception as e:
                print(f"Error updating course in Redis: {e}")

        return updated_course

    async def delete_course(self, course_id: int) -> bool:
        """Delete a course."""
        # In a real implementation, this would delete from a database
        return True

    async def list_courses(self, 
                          skip: int = 0, 
                          limit: int = 100, 
                          filters: Optional[Dict[str, Any]] = None) -> List[Course]:
        """List all courses with pagination and optional filtering."""
        # Initialize empty list for courses
        all_courses = []

        # If Redis manager is available, try to fetch from Redis
        if self.redis_manager and self.redis_manager.is_connected():
            try:
                # Determine which set to use based on filters
                set_key = "all_courses"
                if filters and "featured" in filters and filters["featured"]:
                    set_key = "featured_courses"
                elif filters and "trending" in filters and filters["trending"]:
                    set_key = "trending_courses"

                # Get all course IDs from the appropriate set
                course_ids = self.redis_manager.smembers(set_key)

                # Fetch each course by ID
                for course_id in course_ids:
                    course_key = f"course:{course_id}"
                    course_data = self.redis_manager.get(course_key)
                    if course_data:
                        course_dict = json.loads(course_data)
                        all_courses.append(course_dict)
            except Exception as e:
                print(f"Error fetching courses from Redis: {e}")
                # Fallback to instance variables
                all_courses = self.featured_courses + self.trending_courses
        else:
            # Fallback to instance variables
            all_courses = self.featured_courses + self.trending_courses

        # Apply filters if provided
        if filters:
            # Filter by status if specified
            if "status" in filters:
                all_courses = [c for c in all_courses if c["status"] == filters["status"]]

            # Exclude specific courses if specified
            if "exclude" in filters:
                all_courses = [c for c in all_courses if str(c["id"]) != filters["exclude"]]

        # Apply pagination
        paginated_courses = all_courses[skip:skip + limit]

        # Convert to Course objects and handle datetime conversion
        result = []
        for course in paginated_courses:
            # Convert ISO format strings back to datetime objects if needed
            course_copy = course.copy()
            if isinstance(course_copy.get("created_at"), str):
                course_copy["created_at"] = datetime.fromisoformat(course_copy["created_at"])
            if isinstance(course_copy.get("updated_at"), str):
                course_copy["updated_at"] = datetime.fromisoformat(course_copy["updated_at"])
            if course_copy.get("start_date") and isinstance(course_copy["start_date"], str):
                course_copy["start_date"] = datetime.fromisoformat(course_copy["start_date"])

            result.append(Course(**course_copy))

        return result

    async def publish_course(self, course_id: int) -> Optional[Course]:
        """Change course status to published."""
        # In a real implementation, this would update the course status in a database
        return None

    async def archive_course(self, course_id: int) -> Optional[Course]:
        """Change course status to archived."""
        # In a real implementation, this would update the course status in a database
        return None

    async def get_instructor_courses(self, instructor_id: int) -> List[Course]:
        """Get all courses by a specific instructor from Redis."""
        courses = []
        if self.redis_manager and self.redis_manager.is_connected():
            try:
                course_ids = self.redis_manager.smembers("all_courses")
                for course_id in course_ids:
                    course_key = f"course:{course_id}"
                    course_data = self.redis_manager.get(course_key)
                    if course_data:
                        course_dict = json.loads(course_data)
                        # Match instructor_id
                        if str(course_dict.get("instructor_id")) == str(instructor_id):
                            # Convert datetimes
                            if isinstance(course_dict.get("created_at"), str):
                                course_dict["created_at"] = datetime.fromisoformat(course_dict["created_at"])
                            if isinstance(course_dict.get("updated_at"), str):
                                course_dict["updated_at"] = datetime.fromisoformat(course_dict["updated_at"])
                            if course_dict.get("start_date") and isinstance(course_dict["start_date"], str):
                                course_dict["start_date"] = datetime.fromisoformat(course_dict["start_date"])
                            courses.append(Course(**course_dict))
            except Exception as e:
                print(f"Error fetching instructor courses from Redis: {e}")
        return courses

    async def create_course(self, course_data: dict) -> Course:
        """Create a new course."""
        try:
            if isinstance(course_data.get("level"), str):
                print(f"[DEBUG] level from form: {course_data['level']}")
                course_data["level"] = CourseLevel(course_data["level"].lower())
            if isinstance(course_data.get("status"), str):
                print(f"[DEBUG] status from form: {course_data['status']}")
                course_data["status"] = CourseStatus(course_data["status"].lower())
        except Exception as e:
            print(f"Error converting level/status to Enum: {e}")

        try:
            print(f"[DEBUG] course_data before Course creation: {course_data}")
            course = Course(**course_data)
            print(f"[DEBUG] Course object created: {course}")
        except Exception as e:
            print(f"Error creating Course object: {e}\nData: {course_data}")
            raise

        # Always ensure Redis is connected before saving
        if self.redis_manager:
            try:
                if not self.redis_manager.is_connected():
                    self.redis_manager.connect()
                # Generate a unique ID if not provided
                if course.id is None:
                    course.id = int(datetime.now().timestamp())
                # Convert datetime objects to strings for JSON serialization
                course_dict = course.dict()
                course_dict["created_at"] = course_dict["created_at"].isoformat()
                course_dict["updated_at"] = course_dict["updated_at"].isoformat()
                if course_dict["start_date"]:
                    course_dict["start_date"] = course_dict["start_date"].isoformat()
                # Store individual course
                course_key = f"course:{course.id}"
                result = self.redis_manager.set(course_key, json.dumps(course_dict))
                if not result:
                    print(f"Failed to save course {course.id} to Redis!")
                else:
                    print(f"Course {course.id} saved to Redis")
                # Add to all courses set
                self.redis_manager.sadd("all_courses", course.id)
            except Exception as e:
                print(f"Error saving course to Redis: {e}")
        else:
            print("Redis manager not set on CourseService!")
        return course
