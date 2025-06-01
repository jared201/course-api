from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from services import (
    User, UserRole, UserService,
    Course, CourseLevel, CourseStatus, CourseService,
    Module, Lesson, ContentType, ContentService,
    Enrollment, EnrollmentStatus, EnrollmentService,
    LessonProgress, ModuleProgress, CourseProgress, ProgressService,
    Token, AuthService,
    Payment, PaymentStatus, PaymentMethod, PaymentService
)

app = FastAPI(title="Online Course Platform API")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Add datetime.now function to templates
from datetime import datetime
templates.env.globals["now"] = datetime.now

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize services
user_service = UserService()
course_service = CourseService()
content_service = ContentService()
enrollment_service = EnrollmentService()
progress_service = ProgressService()
auth_service = AuthService()
payment_service = PaymentService()

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Dependency to get the current authenticated user."""
    token_data = await auth_service.verify_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await user_service.get_user(token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint for user authentication and token generation."""
    user_data = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await auth_service.create_access_token(data=user_data)


# User endpoints
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.STUDENT


@app.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    """Create a new user."""
    # In a real implementation, you would hash the password
    user_data = user.dict()
    user_data.pop("password")  # Remove password from response
    return await user_service.create_user(user_data)


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user."""
    return current_user


# Course endpoints
class CourseCreate(BaseModel):
    title: str
    description: str
    level: CourseLevel = CourseLevel.BEGINNER
    price: float = 0.0
    tags: List[str] = []


@app.post("/courses/", response_model=Course)
async def create_course(
    course: CourseCreate, 
    current_user: User = Depends(get_current_user)
):
    """Create a new course."""
    if current_user.role != UserRole.INSTRUCTOR and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors can create courses",
        )

    course_data = course.dict()
    course_data["instructor_id"] = current_user.id
    return await course_service.create_course(course_data)


@app.get("/courses/", response_model=List[Course])
async def list_courses(skip: int = 0, limit: int = 100, exclude: Optional[str] = None):
    """List all published courses."""
    filters = {"status": CourseStatus.PUBLISHED}
    # Handle the exclude parameter if provided
    if exclude:
        filters["exclude"] = exclude
    return await course_service.list_courses(
        skip=skip, 
        limit=limit, 
        filters=filters
    )


@app.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: int):
    """Get a specific course by ID."""
    course = await course_service.get_course(course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    return course


# Root endpoint
@app.get("/")
async def root(request: Request):
    """Root endpoint with API information."""
    # Sample data for featured courses
    featured_courses = [
        {
            "id": 1,
            "title": "Python for Beginners",
            "description": "Learn the basics of Python programming language. This course covers variables, data types, control flow, functions, and more.",
            "instructor_id": 1,
            "level": CourseLevel.BEGINNER,
            "price": 49.99,
            "status": CourseStatus.PUBLISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": ["Python", "Programming", "Beginners"],
            "thumbnail_url": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1074&q=80"
        },
        {
            "id": 2,
            "title": "Web Development with JavaScript",
            "description": "Master JavaScript for web development. Learn DOM manipulation, event handling, AJAX, and modern JavaScript frameworks.",
            "instructor_id": 2,
            "level": CourseLevel.INTERMEDIATE,
            "price": 69.99,
            "status": CourseStatus.PUBLISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": ["JavaScript", "Web Development", "Frontend"],
            "thumbnail_url": "https://images.unsplash.com/photo-1627398242454-45a1465c2479?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1074&q=80"
        },
        {
            "id": 3,
            "title": "Data Science with Python",
            "description": "Explore data science using Python. Learn data analysis, visualization, machine learning, and statistical modeling techniques.",
            "instructor_id": 3,
            "level": CourseLevel.ADVANCED,
            "price": 89.99,
            "status": CourseStatus.PUBLISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": ["Python", "Data Science", "Machine Learning"],
            "thumbnail_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80"
        },
        {
            "id": 4,
            "title": "Mobile App Development with Flutter",
            "description": "Build cross-platform mobile apps with Flutter. Learn Dart programming language and create beautiful, responsive UIs for iOS and Android.",
            "instructor_id": 4,
            "level": CourseLevel.INTERMEDIATE,
            "price": 79.99,
            "status": CourseStatus.PUBLISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": ["Flutter", "Mobile Development", "Dart"],
            "thumbnail_url": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80"
        },
        {
            "id": 5,
            "title": "DevOps and Cloud Computing",
            "description": "Master DevOps practices and cloud computing. Learn CI/CD, containerization, orchestration, and cloud infrastructure management.",
            "instructor_id": 5,
            "level": CourseLevel.ADVANCED,
            "price": 99.99,
            "status": CourseStatus.PUBLISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": ["DevOps", "Cloud Computing", "Docker", "Kubernetes"],
            "thumbnail_url": "https://images.unsplash.com/photo-1667372393119-3d4c48d07fc9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80"
        }
    ]

    # Get trending courses from the hardcoded JSON data
    trending_courses = [
        {
            "id": 101,
            "title": "Machine Learning Fundamentals",
            "description": "Master the core concepts of machine learning. Learn about supervised and unsupervised learning, neural networks, and practical applications.",
            "instructor_id": 10,
            "level": CourseLevel.INTERMEDIATE,
            "price": 79.99,
            "status": CourseStatus.PUBLISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": ["Machine Learning", "AI", "Data Science", "Python"],
            "thumbnail_url": "https://images.unsplash.com/photo-1527474305487-b87b222841cc?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1074&q=80"
        },
        {
            "id": 102,
            "title": "Full Stack Web Development",
            "description": "Become a full stack developer. Learn frontend technologies like React, backend with Node.js, and database management with MongoDB.",
            "instructor_id": 11,
            "level": CourseLevel.ADVANCED,
            "price": 89.99,
            "status": CourseStatus.PUBLISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": ["Web Development", "JavaScript", "React", "Node.js", "MongoDB"],
            "thumbnail_url": "https://images.unsplash.com/photo-1547658719-da2b51169166?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1074&q=80"
        },
        {
            "id": 103,
            "title": "Blockchain and Cryptocurrency",
            "description": "Understand blockchain technology and cryptocurrency. Learn about smart contracts, decentralized applications, and the future of finance.",
            "instructor_id": 12,
            "level": CourseLevel.INTERMEDIATE,
            "price": 99.99,
            "status": CourseStatus.PUBLISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": ["Blockchain", "Cryptocurrency", "Smart Contracts", "Ethereum"],
            "thumbnail_url": "https://images.unsplash.com/photo-1639762681057-408e52192e55?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1074&q=80"
        },
        {
            "id": 104,
            "title": "UX/UI Design Masterclass",
            "description": "Create beautiful and functional user interfaces. Learn design principles, prototyping, user research, and industry-standard tools.",
            "instructor_id": 13,
            "level": CourseLevel.BEGINNER,
            "price": 69.99,
            "status": CourseStatus.PUBLISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": ["UX Design", "UI Design", "Figma", "Adobe XD", "Prototyping"],
            "thumbnail_url": "https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80"
        },
        {
            "id": 105,
            "title": "Cybersecurity Essentials",
            "description": "Protect systems and networks from digital attacks. Learn about encryption, network security, ethical hacking, and security best practices.",
            "instructor_id": 14,
            "level": CourseLevel.ADVANCED,
            "price": 109.99,
            "status": CourseStatus.PUBLISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": ["Cybersecurity", "Network Security", "Ethical Hacking", "Encryption"],
            "thumbnail_url": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80"
        }
    ]

    return templates.TemplateResponse("base.html", {
        "request": request,
        "title": "Welcome to the Online Course Platform",
        "message": "Welcome to the Online Course Platform API",
        "version": "1.0.0",
        "documentation": "/docs",
        "featured_courses": featured_courses,
        "trending_courses": trending_courses,
    })

# HTML UI routes
@app.get("/courses/ui", response_class=HTMLResponse)
async def list_courses_ui(request: Request, skip: int = 0, limit: int = 100, exclude: Optional[str] = None):
    """List all published courses with HTML UI."""
    filters = {"status": CourseStatus.PUBLISHED}
    # Handle the exclude parameter if provided
    if exclude:
        filters["exclude"] = exclude
    courses = await course_service.list_courses(
        skip=skip, 
        limit=limit, 
        filters=filters
    )
    return templates.TemplateResponse("courses/list.html", {
        "request": request,
        "courses": courses
    })

@app.get("/courses/{course_id}/ui", response_class=HTMLResponse)
async def get_course_ui(request: Request, course_id: int):
    """Get a specific course by ID with HTML UI."""
    course = await course_service.get_course(course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    return templates.TemplateResponse("courses/detail.html", {
        "request": request,
        "course": course
    })

@app.get("/courses/{course_id}/modules/{module_id}/ui", response_class=HTMLResponse)
async def get_module_ui(request: Request, course_id: int, module_id: int):
    """Get a specific module by ID with HTML UI."""
    course = await course_service.get_course(course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    module = await content_service.get_module(module_id)
    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found",
        )

    return templates.TemplateResponse("modules/detail.html", {
        "request": request,
        "course": course,
        "module": module,
        "completed_lessons": []  # This would be populated from user progress
    })

@app.get("/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/ui", response_class=HTMLResponse)
async def get_lesson_ui(request: Request, course_id: int, module_id: int, lesson_id: int):
    """Get a specific lesson by ID with HTML UI."""
    course = await course_service.get_course(course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    module = await content_service.get_module(module_id)
    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found",
        )

    lesson = await content_service.get_lesson(lesson_id)
    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )

    return templates.TemplateResponse("lessons/detail.html", {
        "request": request,
        "course": course,
        "module": module,
        "lesson": lesson,
        "completed_lessons": []  # This would be populated from user progress
    })


@app.get("/api/trending-courses", response_model=List[Course])
async def get_trending_courses():
    """Get a list of trending courses."""
    # Sample data for trending courses
    trending_courses = [
        {
            "id": 101,
            "title": "Machine Learning Fundamentals",
            "description": "Master the core concepts of machine learning. Learn about supervised and unsupervised learning, neural networks, and practical applications.",
            "instructor_id": 10,
            "level": CourseLevel.INTERMEDIATE,
            "price": 79.99,
            "status": CourseStatus.PUBLISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": ["Machine Learning", "AI", "Data Science", "Python"],
            "thumbnail_url": "https://images.unsplash.com/photo-1527474305487-b87b222841cc?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1074&q=80"
        },
        {
            "id": 102,
            "title": "Full Stack Web Development",
            "description": "Become a full stack developer. Learn frontend technologies like React, backend with Node.js, and database management with MongoDB.",
            "instructor_id": 11,
            "level": CourseLevel.ADVANCED,
            "price": 89.99,
            "status": CourseStatus.PUBLISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": ["Web Development", "JavaScript", "React", "Node.js", "MongoDB"],
            "thumbnail_url": "https://images.unsplash.com/photo-1547658719-da2b51169166?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1074&q=80"
        },
        {
            "id": 103,
            "title": "Blockchain and Cryptocurrency",
            "description": "Understand blockchain technology and cryptocurrency. Learn about smart contracts, decentralized applications, and the future of finance.",
            "instructor_id": 12,
            "level": CourseLevel.INTERMEDIATE,
            "price": 99.99,
            "status": CourseStatus.PUBLISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": ["Blockchain", "Cryptocurrency", "Smart Contracts", "Ethereum"],
            "thumbnail_url": "https://images.unsplash.com/photo-1639762681057-408e52192e55?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1074&q=80"
        },
        {
            "id": 104,
            "title": "UX/UI Design Masterclass",
            "description": "Create beautiful and functional user interfaces. Learn design principles, prototyping, user research, and industry-standard tools.",
            "instructor_id": 13,
            "level": CourseLevel.BEGINNER,
            "price": 69.99,
            "status": CourseStatus.PUBLISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": ["UX Design", "UI Design", "Figma", "Adobe XD", "Prototyping"],
            "thumbnail_url": "https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80"
        },
        {
            "id": 105,
            "title": "Cybersecurity Essentials",
            "description": "Protect systems and networks from digital attacks. Learn about encryption, network security, ethical hacking, and security best practices.",
            "instructor_id": 14,
            "level": CourseLevel.ADVANCED,
            "price": 109.99,
            "status": CourseStatus.PUBLISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": ["Cybersecurity", "Network Security", "Ethical Hacking", "Encryption"],
            "thumbnail_url": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80"
        }
    ]

    return trending_courses
