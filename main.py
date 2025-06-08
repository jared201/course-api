from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
import json

from services import (
    User, UserRole, UserService,
    Course, CourseLevel, CourseStatus, CourseService,
    Module, Lesson, ContentType, ContentService,
    Enrollment, EnrollmentStatus, EnrollmentService,
    LessonProgress, ModuleProgress, CourseProgress, ProgressService,
    Token, AuthService,
    Payment, PaymentStatus, PaymentMethod, PaymentService
)
from services.redis_manager import RedisManager

app = FastAPI(title="Online Course Platform API")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Initialize Redis manager
redis_manager = RedisManager()

# Add datetime.now function to templates
from datetime import datetime

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
        "start_date": datetime.now().replace(day=1, month=datetime.now().month + 1 if datetime.now().month < 12 else 1),
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
        "start_date": datetime.now().replace(day=15, month=datetime.now().month + 1 if datetime.now().month < 12 else 1),
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
        "start_date": datetime.now().replace(day=1, month=(datetime.now().month + 2) % 12 or 12),
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
        "start_date": datetime.now().replace(day=15, month=(datetime.now().month + 2) % 12 or 12),
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
        "start_date": datetime.now().replace(day=1, month=(datetime.now().month + 3) % 12 or 12),
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
        "start_date": datetime.now().replace(day=10, month=datetime.now().month + 1 if datetime.now().month < 12 else 1),
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
        "start_date": datetime.now().replace(day=20, month=datetime.now().month + 1 if datetime.now().month < 12 else 1),
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
        "start_date": datetime.now().replace(day=5, month=(datetime.now().month + 2) % 12 or 12),
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
        "start_date": datetime.now().replace(day=25, month=(datetime.now().month + 2) % 12 or 12),
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
        "start_date": datetime.now().replace(day=15, month=(datetime.now().month + 3) % 12 or 12),
        "tags": ["Cybersecurity", "Network Security", "Ethical Hacking", "Encryption"],
        "thumbnail_url": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80"
    }
]
templates.env.globals["now"] = datetime.now

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize services
user_service = UserService()
course_service = CourseService(featured_courses=featured_courses, trending_courses=trending_courses, redis_manager=redis_manager)
content_service = ContentService()
enrollment_service = EnrollmentService()
progress_service = ProgressService()
auth_service = AuthService()
payment_service = PaymentService()

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Dependency to get the current authenticated user from Authorization header."""
    return await authenticate_user_with_token(token)


async def authenticate_user_with_token(token: str) -> User:
    """Authenticate a user with a token."""
    token_data = await auth_service.verify_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Special case for admin user
    if token_data.username == "admin" and token_data.role == UserRole.ADMIN:
        user = User(
            id=token_data.user_id,
            username=token_data.username,
            email="admin@example.com",
            full_name="Admin User",
            role=UserRole.ADMIN
        )
        return user

    # Get the user directly by username from Redis
    user = await user_service.get_user_by_username(token_data.username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Ensure the user's role is set from the token data
    # This is important since we're now using the role from the token
    user.role = token_data.role

    return user


async def get_current_user_from_cookie(request: Request, response: Optional[Response] = None) -> User:
    """Dependency to get the current authenticated user from cookie."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Remove 'Bearer ' prefix if present
    if token.startswith("Bearer "):
        token = token[7:]

    user = await authenticate_user_with_token(token)
    print(f"User: {user}")
    # Update the cookie if a response is provided
    if response and token:
        # Create a new token with updated expiration
        user_data = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role
        }
        new_token = await auth_service.create_access_token(data=user_data)

        # Set the updated token in the cookie
        response.set_cookie(
            key="access_token",
            value=f"Bearer {new_token.access_token}",
            httponly=True,
            max_age=1800,  # 30 minutes
            expires=new_token.expires_at.timestamp()
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
    # Don't remove password, let UserService handle it
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
async def root(request: Request, response: Response):
    """Root endpoint with API information."""

    # Try to get the current user from cookie
    user = None
    try:
        user = await get_current_user_from_cookie(request, response)
    except HTTPException:
        # User is not authenticated, continue without user
        pass

    return templates.TemplateResponse("base.html", {
        "request": request,
        "title": "Welcome to the Online Course Platform",
        "message": "Welcome to the Online Course Platform API",
        "version": "1.0.0",
        "documentation": "/docs",
        "featured_courses": featured_courses,
        "trending_courses": trending_courses,
        "user": user
    })

# HTML UI routes
@app.get("/courses", response_class=HTMLResponse)
@app.get("/courses/ui", response_class=HTMLResponse)
async def list_courses_ui(request: Request, response: Response, skip: int = 0, limit: int = 100, exclude: Optional[str] = None, featured: bool = False, trending: bool = False):
    """List all published courses with HTML UI."""
    filters = {"status": CourseStatus.PUBLISHED}
    # Handle the exclude parameter if provided and not empty
    if exclude and exclude.strip():
        filters["exclude"] = exclude

    # Add featured or trending filters if specified
    if featured:
        filters["featured"] = True
    elif trending:
        filters["trending"] = True

    courses = await course_service.list_courses(
        skip=skip, 
        limit=limit, 
        filters=filters
    )

    # Get featured and trending courses separately for the template
    featured_filters = {"status": CourseStatus.PUBLISHED, "featured": True}
    trending_filters = {"status": CourseStatus.PUBLISHED, "trending": True}

    featured_courses_list = await course_service.list_courses(filters=featured_filters)
    trending_courses_list = await course_service.list_courses(filters=trending_filters)

    # Try to get the current user from cookie
    user = None
    try:
        user = await get_current_user_from_cookie(request, response)
    except HTTPException:
        # User is not authenticated, continue without user
        pass

    return templates.TemplateResponse("courses/list.html", {
        "request": request,
        "courses": courses,
        "featured_courses": featured_courses_list,
        "trending_courses": trending_courses_list,
        "user": user
    })

@app.get("/courses/{course_id}/ui", response_class=HTMLResponse)
async def get_course_ui(request: Request, response: Response, course_id: int):
    """Get a specific course by ID with HTML UI."""
    # Get the course using the course service
    course = await course_service.get_course(course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    # Convert Pydantic model to dict for template
    course = course.dict()

    # Generate sample modules and lessons for the course
    modules = [
        {
            "id": 1,
            "course_id": course_id,
            "title": "Introduction to " + course["title"],
            "description": "Get started with the basics of " + course["title"],
            "order": 1,
            "lessons": [
                {
                    "id": 1,
                    "module_id": 1,
                    "title": "Welcome to the Course",
                    "description": "Introduction to the course",
                    "content_type": ContentType.VIDEO,
                    "content": "https://example.com/video1.mp4",
                    "duration_minutes": 10,
                    "order": 1,
                    "is_free_preview": True
                },
                {
                    "id": 2,
                    "module_id": 1,
                    "title": "Course Overview",
                    "description": "Overview of what you'll learn",
                    "content_type": ContentType.TEXT,
                    "content": "This is the course overview text content.",
                    "order": 2,
                    "is_free_preview": True
                }
            ]
        },
        {
            "id": 2,
            "course_id": course_id,
            "title": "Core Concepts",
            "description": "Learn the fundamental concepts of " + course["title"],
            "order": 2,
            "lessons": [
                {
                    "id": 3,
                    "module_id": 2,
                    "title": "Key Principles",
                    "description": "Understanding the key principles",
                    "content_type": ContentType.VIDEO,
                    "content": "https://example.com/video2.mp4",
                    "duration_minutes": 15,
                    "order": 1,
                    "is_free_preview": False
                },
                {
                    "id": 4,
                    "module_id": 2,
                    "title": "Practice Quiz",
                    "description": "Test your knowledge",
                    "content_type": ContentType.QUIZ,
                    "content": "{'questions': [...]}",  # JSON string for quiz questions
                    "order": 2,
                    "is_free_preview": False
                }
            ]
        }
    ]

    # Add modules to the course
    course_with_modules = course.copy()
    course_with_modules["modules"] = modules

    # Add instructor information
    course_with_modules["instructor"] = {
        "id": course["instructor_id"],
        "full_name": f"Instructor {course['instructor_id']}",  # Mock instructor name
        "email": f"instructor{course['instructor_id']}@example.com",
        "bio": "Experienced instructor with expertise in this subject."
    }

    # Add duration information
    course_with_modules["duration"] = 12  # Mock duration in hours

    # Add enrolled_students field
    course_with_modules["enrolled_students"] = []  # Empty list by default

    # Try to get the current user from cookie
    user = None
    try:
        user = await get_current_user_from_cookie(request, response)
    except HTTPException:
        # User is not authenticated, continue without user
        pass

    return templates.TemplateResponse("courses/detail.html", {
        "request": request,
        "course": course_with_modules,
        "featured_courses": featured_courses,
        "trending_courses": trending_courses,
        "user": user
    })

@app.get("/courses/{course_id}/modules/{module_id}/ui", response_class=HTMLResponse)
async def get_module_ui(request: Request, response: Response, course_id: int, module_id: int):
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

    # Try to get the current user from cookie
    user = None
    try:
        user = await get_current_user_from_cookie(request, response)
    except HTTPException:
        # User is not authenticated, continue without user
        pass

    return templates.TemplateResponse("modules/detail.html", {
        "request": request,
        "course": course,
        "module": module,
        "completed_lessons": [],  # This would be populated from user progress
        "featured_courses": featured_courses,
        "trending_courses": trending_courses,
        "user": user
    })

@app.get("/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/ui", response_class=HTMLResponse)
async def get_lesson_ui(request: Request, response: Response, course_id: int, module_id: int, lesson_id: int):
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

    # Try to get the current user from cookie
    user = None
    try:
        user = await get_current_user_from_cookie(request, response)
    except HTTPException:
        # User is not authenticated, continue without user
        pass

    return templates.TemplateResponse("lessons/detail.html", {
        "request": request,
        "course": course,
        "module": module,
        "lesson": lesson,
        "completed_lessons": [],  # This would be populated from user progress
        "featured_courses": featured_courses,
        "trending_courses": trending_courses,
        "user": user
    })

@app.get("/login", response_class=HTMLResponse)
async def login_ui(request: Request, response: Response):
    """Render the login page."""
    # Check if user is already logged in
    try:
        user = await get_current_user_from_cookie(request, response)
        # If we get here, user is logged in, redirect to home page
        return RedirectResponse(url="/", status_code=303)
    except HTTPException:
        # User is not logged in, show login page
        pass

    return templates.TemplateResponse("login.html", {
        "request": request,
        "featured_courses": featured_courses,
        "trending_courses": trending_courses
    })


@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    """Log out the current user by clearing the cookie."""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    return response

@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Handle login form submission."""
    # Authenticate user
    user_data = await auth_service.authenticate_user(username, password)
    if not user_data:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password",
            "username": username,
            "featured_courses": featured_courses,
            "trending_courses": trending_courses
        })

    # Create access token
    token = await auth_service.create_access_token(data=user_data)

    # Set the token in a cookie
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token.access_token}",
        httponly=True,
        max_age=1800,  # 30 minutes
        expires=token.expires_at.timestamp()
    )

    # Redirect to home page or dashboard
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_ui(request: Request, response: Response):
    """Render the registration page."""
    # Check if user is already logged in
    try:
        user = await get_current_user_from_cookie(request, response)
        # If we get here, user is logged in, redirect to home page
        return RedirectResponse(url="/", status_code=303)
    except HTTPException:
        # User is not logged in, show registration page
        pass

    return templates.TemplateResponse("register.html", {
        "request": request,
        "featured_courses": featured_courses,
        "trending_courses": trending_courses
    })

@app.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    role: str = Form(...)
):
    """Handle registration form submission."""
    # Check if passwords match
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Passwords do not match",
            "username": username,
            "email": email,
            "full_name": full_name,
            "featured_courses": featured_courses,
            "trending_courses": trending_courses
        })

    # Create user
    try:
        # Check if user with this username already exists
        existing_user = await user_service.get_user_by_username(username)
        if existing_user:
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Username already exists",
                "email": email,
                "full_name": full_name,
                "featured_courses": featured_courses,
                "trending_courses": trending_courses
            })

        # Prepare user data for creation
        user_data = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "password": password,
            "role": role
        }
        # Directly pass the dictionary to create_user method
        created_user = await user_service.create_user(user_data)

        # Log the user in by creating an access token
        user_token_data = {
            "user_id": created_user.id,
            "username": created_user.username,
            "role": created_user.role
        }
        token = await auth_service.create_access_token(data=user_token_data)

        # Set the token in a cookie and redirect to home page
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {token.access_token}",
            httponly=True,
            max_age=1800,  # 30 minutes
            expires=token.expires_at.timestamp()
        )
        return response
    except Exception as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": str(e),
            "username": username,
            "email": email,
            "full_name": full_name,
            "featured_courses": featured_courses,
            "trending_courses": trending_courses
        })


@app.get("/api/courses/{course_id}/overview")
async def get_course_overview(course_id: int):
    """Get a course overview with modules and lessons."""
    # In a real implementation, this would fetch the course, modules, and lessons from a database
    # For now, we'll return mock data

    # Find the course in the featured_courses or trending_courses arrays
    course = None
    for c in featured_courses:
        if c["id"] == course_id:
            course = c
            break

    if not course:
        for c in trending_courses:
            if c["id"] == course_id:
                course = c
                break

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    # Generate sample modules and lessons for the course
    modules = [
        {
            "id": 1,
            "course_id": course_id,
            "title": "Introduction to " + course["title"],
            "description": "Get started with the basics of " + course["title"],
            "order": 1,
            "lessons": [
                {
                    "id": 1,
                    "module_id": 1,
                    "title": "Welcome to the Course",
                    "description": "Introduction to the course",
                    "content_type": ContentType.VIDEO,
                    "content": "https://example.com/video1.mp4",
                    "duration_minutes": 10,
                    "order": 1,
                    "is_free_preview": True
                },
                {
                    "id": 2,
                    "module_id": 1,
                    "title": "Course Overview",
                    "description": "Overview of what you'll learn",
                    "content_type": ContentType.TEXT,
                    "content": "This is the course overview text content.",
                    "order": 2,
                    "is_free_preview": True
                }
            ]
        },
        {
            "id": 2,
            "course_id": course_id,
            "title": "Core Concepts",
            "description": "Learn the fundamental concepts of " + course["title"],
            "order": 2,
            "lessons": [
                {
                    "id": 3,
                    "module_id": 2,
                    "title": "Key Principles",
                    "description": "Understanding the key principles",
                    "content_type": ContentType.VIDEO,
                    "content": "https://example.com/video2.mp4",
                    "duration_minutes": 15,
                    "order": 1,
                    "is_free_preview": False
                },
                {
                    "id": 4,
                    "module_id": 2,
                    "title": "Practice Quiz",
                    "description": "Test your knowledge",
                    "content_type": ContentType.QUIZ,
                    "content": "{'questions': [...]}",  # JSON string for quiz questions
                    "order": 2,
                    "is_free_preview": False
                }
            ]
        }
    ]

    # Add modules to the course
    course_with_modules = course.copy()
    course_with_modules["modules"] = modules

    return course_with_modules


@app.get("/api/trending-courses", response_model=List[Course])
async def get_trending_courses():
    """Get a list of trending courses."""
    # Use the global trending_courses variable
    return trending_courses


@app.post("/courses/{course_id}/enroll")
async def enroll_in_course(course_id: int, current_user: User = Depends(get_current_user)):
    """Enroll the current user in a course."""
    # Check if the course exists
    course = await course_service.get_course(course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    # Check if the user is already enrolled
    is_enrolled = await enrollment_service.is_user_enrolled(current_user.id, course_id)
    if is_enrolled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already enrolled in this course",
        )

    # Enroll the user
    enrollment = await enrollment_service.enroll_user(current_user.id, course_id)
    return {"status": "success", "message": "Successfully enrolled in the course"}


@app.post("/admin/courses/move-to-redis")
async def move_courses_to_redis(current_user: User = Depends(get_current_user)):
    """
    Move all course data to Redis.
    This endpoint is for administrative purposes and should be called with caution.
    """
    # Check if user is an admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this operation",
        )

    # Check if Redis is connected
    if not redis_manager.is_connected():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Redis connection is not available",
        )

    # Store featured courses in Redis
    featured_courses_key = "featured_courses"
    for i, course in enumerate(featured_courses):
        # Convert datetime objects to strings for JSON serialization
        course_copy = course.copy()
        course_copy["created_at"] = course_copy["created_at"].isoformat()
        course_copy["updated_at"] = course_copy["updated_at"].isoformat()
        if course_copy["start_date"]:
            course_copy["start_date"] = course_copy["start_date"].isoformat()

        # Store individual course
        course_key = f"course:{course['id']}"
        redis_manager.set(course_key, json.dumps(course_copy))

        # Add to featured courses set
        redis_manager.sadd(featured_courses_key, course['id'])

    # Store trending courses in Redis
    trending_courses_key = "trending_courses"
    for i, course in enumerate(trending_courses):
        # Convert datetime objects to strings for JSON serialization
        course_copy = course.copy()
        course_copy["created_at"] = course_copy["created_at"].isoformat()
        course_copy["updated_at"] = course_copy["updated_at"].isoformat()
        if course_copy["start_date"]:
            course_copy["start_date"] = course_copy["start_date"].isoformat()

        # Store individual course
        course_key = f"course:{course['id']}"
        redis_manager.set(course_key, json.dumps(course_copy))

        # Add to trending courses set
        redis_manager.sadd(trending_courses_key, course['id'])

    # Store all course IDs in a set
    all_courses_key = "all_courses"
    all_course_ids = [course["id"] for course in featured_courses + trending_courses]
    redis_manager.sadd(all_courses_key, *all_course_ids)

    return JSONResponse(content={
        "status": "success",
        "message": "All course data has been moved to Redis",
        "details": {
            "featured_courses": len(featured_courses),
            "trending_courses": len(trending_courses),
            "total_courses": len(all_course_ids)
        }
    })


@app.get("/my-courses", response_class=HTMLResponse)
async def my_courses(request: Request, response: Response):
    """Show the current user's enrolled courses."""
    # Try to get the current user from cookie
    try:
        user = await get_current_user_from_cookie(request, response)

        # Check if user is a student
        if user.role != UserRole.STUDENT:
            print(f"User is not a student - redirecting to home page: {user.username}")
            print(f"User role: {user.role}")
            return RedirectResponse(url="/", status_code=303)

        # Get the user's enrollments
        enrollments = await enrollment_service.get_user_enrollments(user.id)

        # Separate enrollments into active and completed
        active_enrollments = [e for e in enrollments if e.status == EnrollmentStatus.ACTIVE]
        completed_enrollments = [e for e in enrollments if e.status == EnrollmentStatus.COMPLETED]

        # Get course details for each enrollment
        enrolled_courses = []
        for enrollment in active_enrollments:
            course = await course_service.get_course(enrollment.course_id)
            if course:
                # Add enrollment information to the course
                course_dict = course.dict()
                course_dict["enrolled_at"] = enrollment.enrolled_at
                enrolled_courses.append(course_dict)

        completed_courses = []
        for enrollment in completed_enrollments:
            course = await course_service.get_course(enrollment.course_id)
            if course:
                # Add enrollment information to the course
                course_dict = course.dict()
                course_dict["enrolled_at"] = enrollment.enrolled_at
                course_dict["completed_at"] = enrollment.completed_at
                completed_courses.append(course_dict)

        # No need to get featured courses for dashboard
        featured_courses_list = []
        print(f"Dashboard: {featured_courses_list}")
        return templates.TemplateResponse("my_courses.html", {
            "request": request,
            "user": user,
            "enrolled_courses": enrolled_courses,
            "completed_courses": completed_courses,
            "featured_courses": featured_courses_list
        })
    except HTTPException:
        # User is not authenticated, redirect to login
        return RedirectResponse(url="/login", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, response: Response):
    """Redirect to the appropriate dashboard based on user role."""
    try:
        user = await get_current_user_from_cookie(request, response)

        # Redirect to appropriate dashboard based on role
        if user.role == UserRole.STUDENT:
            print(f"Redirecting to dashboard for student: {user.username}")
            return RedirectResponse(url="/my-courses", status_code=303)
        elif user.role == UserRole.INSTRUCTOR:
            return RedirectResponse(url="/my-lessons", status_code=303)
        else:
            # Admin or other roles
            return RedirectResponse(url="/", status_code=303)
    except HTTPException:
        # User is not authenticated, redirect to login
        return RedirectResponse(url="/login", status_code=303)


@app.get("/my-lessons", response_class=HTMLResponse)
async def my_lessons(request: Request, response: Response):
    """Show the current instructor's courses."""
    # Try to get the current user from cookie
    try:
        user = await get_current_user_from_cookie(request, response)

        # Check if user is an instructor
        if user.role != UserRole.INSTRUCTOR:
            return RedirectResponse(url="/", status_code=303)

        # Get instructor's courses from Redis
        courses = await course_service.get_instructor_courses(user.id)

        # Convert Pydantic models to dicts for template
        course_dicts = [course.dict() for course in courses]

        # Sort courses by created_at (newest first)
        course_dicts.sort(key=lambda x: x["created_at"], reverse=True)

        return templates.TemplateResponse("my_lessons.html", {
            "request": request,
            "user": user,
            "courses": course_dicts,
            "featured_courses": [],
            "trending_courses": []
        })
    except HTTPException:
        # User is not authenticated, redirect to login
        return RedirectResponse(url="/login", status_code=303)


@app.get("/create-lesson", response_class=HTMLResponse)
async def create_lesson_form(request: Request, response: Response):
    """Render the create lesson form."""
    try:
        user = await get_current_user_from_cookie(request, response)

        # Check if user is an instructor
        if user.role != UserRole.INSTRUCTOR:
            return RedirectResponse(url="/", status_code=303)

        # Get modules for the dropdown
        # In a real implementation, you would fetch modules from a database
        # For now, we'll use sample modules
        modules = [
            {
                "id": 1,
                "title": "Introduction to Programming"
            },
            {
                "id": 2,
                "title": "Core Concepts"
            },
            {
                "id": 3,
                "title": "Advanced Topics"
            }
        ]

        return templates.TemplateResponse("lessons/create_lesson.html", {
            "request": request,
            "user": user,
            "modules": modules,
            "featured_courses": [],
            "trending_courses": []
        })
    except HTTPException:
        # User is not authenticated, redirect to login
        return RedirectResponse(url="/login", status_code=303)


@app.get("/create-course", response_class=HTMLResponse)
async def create_course_form(request: Request, response: Response):
    """Render the create course form."""
    try:
        user = await get_current_user_from_cookie(request, response)

        # Check if user is an instructor
        if user.role != UserRole.INSTRUCTOR:
            return RedirectResponse(url="/", status_code=303)

        return templates.TemplateResponse("courses/create_course.html", {
            "request": request,
            "user": user,
            "featured_courses": [],
            "trending_courses": []
        })
    except HTTPException:
        # User is not authenticated, redirect to login
        return RedirectResponse(url="/login", status_code=303)


@app.post("/create-course", response_class=HTMLResponse)
async def create_course_submit(
    request: Request,
    response: Response,
    title: str = Form(...),
    description: str = Form(...),
    level: str = Form(...),
    price: float = Form(0.0),
    tags: str = Form(""),
    thumbnail_url: Optional[str] = Form(None),
    start_date: Optional[str] = Form(None),
    status: str = Form("pending"),
):
    """Handle course form submission."""
    try:
        user = await get_current_user_from_cookie(request, response)

        # Check if user is an instructor
        if user.role != UserRole.INSTRUCTOR:
            return RedirectResponse(url="/", status_code=303)

        # Parse start_date string to datetime if provided
        from datetime import datetime
        parsed_start_date = None
        if start_date:
            try:
                parsed_start_date = datetime.fromisoformat(start_date)
            except Exception as e:
                print(f"Invalid start_date format: {start_date} - {e}")

        # Process tags (convert comma-separated string to list)
        tags_list = [tag.strip() for tag in tags.split(",")] if tags else []

        # Create course data dictionary
        course_data = {
            "title": title,
            "description": description,
            "level": level,
            "price": price,
            "tags": tags_list,
            "thumbnail_url": thumbnail_url,
            "start_date": parsed_start_date,
            "instructor_id": user.id,
            "status": status
        }

        # Create the course
        course = await course_service.create_course(course_data)

        # Process module and lesson data
        form = await request.form()

        # Get all module titles and descriptions
        module_titles = form.getlist("module_titles[]")
        module_descriptions = form.getlist("module_descriptions[]")

        # Get all lesson data
        lesson_titles = form.getlist("lesson_titles[]")
        lesson_descriptions = form.getlist("lesson_descriptions[]")
        lesson_content_types = form.getlist("lesson_content_types[]")
        lesson_contents = form.getlist("lesson_contents[]")
        lesson_durations = form.getlist("lesson_durations[]")
        lesson_free_previews = form.getlist("lesson_free_previews[]")

        # Initialize content service
        content_service = ContentService()

        # Track current lesson index
        lesson_index = 0

        # Create modules and their lessons
        for i in range(len(module_titles)):
            if module_titles[i].strip():  # Only create module if title is not empty
                # Create module
                module_data = {
                    "course_id": course.id,
                    "title": module_titles[i],
                    "description": module_descriptions[i] if i < len(module_descriptions) else "",
                    "order": i + 1
                }
                module = await content_service.create_module(module_data)

                # Count lessons in this module
                module_lesson_count = 0

                # Find lessons for this module
                while lesson_index < len(lesson_titles):
                    if lesson_titles[lesson_index].strip():  # Only create lesson if title is not empty
                        # Create lesson
                        lesson_data = {
                            "module_id": module.id,
                            "title": lesson_titles[lesson_index],
                            "description": lesson_descriptions[lesson_index] if lesson_index < len(lesson_descriptions) else "",
                            "content_type": lesson_content_types[lesson_index] if lesson_index < len(lesson_content_types) else "text",
                            "content": lesson_contents[lesson_index] if lesson_index < len(lesson_contents) else "",
                            "duration_minutes": int(lesson_durations[lesson_index]) if lesson_index < len(lesson_durations) and lesson_durations[lesson_index] else None,
                            "is_free_preview": str(lesson_index) in lesson_free_previews,
                            "order": module_lesson_count + 1
                        }
                        await content_service.create_lesson(lesson_data)
                        module_lesson_count += 1

                    lesson_index += 1

                    # If we've reached the end of this module's lessons or processed at least one lesson
                    # and there are more modules to process, break to the next module
                    if (module_lesson_count > 0 and i < len(module_titles) - 1 and 
                        lesson_index < len(lesson_titles) - 1 and 
                        lesson_titles[lesson_index + 1].strip() and
                        module_titles[i + 1].strip()):
                        break

        # Redirect to my-lessons page
        return RedirectResponse(url="/my-lessons", status_code=303)
    except HTTPException as e:
        # Handle errors
        return templates.TemplateResponse("courses/create_course.html", {
            "request": request,
            "user": user,
            "error": e.detail,
            "featured_courses": [],
            "trending_courses": []
        })
    except Exception as e:
        # Handle unexpected errors
        return templates.TemplateResponse("courses/create_course.html", {
            "request": request,
            "user": user,
            "error": str(e),
            "featured_courses": [],
            "trending_courses": []
        })


@app.post("/create-lesson", response_class=HTMLResponse)
async def create_lesson(
    request: Request,
    response: Response,
    module_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    content_type: str = Form(...),
    order: int = Form(...),
    is_free_preview: bool = Form(False),
    image_url: Optional[str] = Form(None),
    duration_minutes: Optional[int] = Form(None),
    topic_titles: List[str] = Form([]),
    topic_contents: List[str] = Form([])
):
    """Handle lesson form submission."""
    try:
        user = await get_current_user_from_cookie(request, response)

        # Check if user is an instructor
        if user.role != UserRole.INSTRUCTOR:
            return RedirectResponse(url="/", status_code=303)

        # Process content based on content_type
        content = ""
        form = await request.form()

        if content_type == "video":
            content = form.get("video_url", "")
        elif content_type == "text":
            content = form.get("text_content", "")
        elif content_type == "quiz":
            # Process quiz questions
            quiz_questions = form.getlist("quiz_questions[]")
            quiz_options = form.getlist("quiz_options[]")
            quiz_answers = form.getlist("quiz_answers[]")

            quiz_data = []
            for i in range(len(quiz_questions)):
                if i < len(quiz_questions) and quiz_questions[i]:
                    options = quiz_options[i].split('\n') if i < len(quiz_options) else []
                    answer = quiz_answers[i] if i < len(quiz_answers) else ""
                    quiz_data.append({
                        "question": quiz_questions[i],
                        "options": options,
                        "answer": answer
                    })

            content = json.dumps(quiz_data)
        elif content_type == "assignment":
            instructions = form.get("assignment_instructions", "")
            due_date = form.get("assignment_due_date", "")
            content = json.dumps({
                "instructions": instructions,
                "due_date": due_date
            })
        elif content_type == "file":
            # In a real implementation, you would upload the file to a storage service
            # and store the URL in content
            content = "file_url_placeholder"

        # Process image
        image = ""
        if image_url:
            image = image_url
        elif "image_upload" in form:
            # In a real implementation, you would upload the image to a storage service
            # and store the URL in image
            image = "image_url_placeholder"

        # Process topics
        topics = []
        for i in range(len(topic_titles)):
            if i < len(topic_titles) and topic_titles[i]:
                topic_content = topic_contents[i] if i < len(topic_contents) else ""
                topics.append({
                    "title": topic_titles[i],
                    "content": topic_content
                })

        # Create lesson data
        lesson_data = {
            "module_id": module_id,
            "title": title,
            "description": description,
            "content_type": content_type,
            "content": content,
            "duration_minutes": duration_minutes,
            "order": order,
            "is_free_preview": is_free_preview,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "image": image,
            "topics": topics
        }

        # Save lesson to Redis
        lesson_id = int(datetime.now().timestamp())  # Generate a unique ID
        lesson_key = f"lesson:{lesson_id}"

        # Convert datetime objects to strings for JSON serialization
        lesson_data_copy = lesson_data.copy()
        lesson_data_copy["created_at"] = lesson_data_copy["created_at"].isoformat()
        lesson_data_copy["updated_at"] = lesson_data_copy["updated_at"].isoformat()

        # Store lesson in Redis
        redis_manager.set(lesson_key, json.dumps(lesson_data_copy))

        # Add lesson ID to module's lessons set
        module_lessons_key = f"module:{module_id}:lessons"
        redis_manager.sadd(module_lessons_key, lesson_id)

        # Add lesson ID to instructor's lessons set
        instructor_lessons_key = f"instructor:{user.id}:lessons"
        redis_manager.sadd(instructor_lessons_key, lesson_id)

        # Redirect to my lessons page
        return RedirectResponse(url="/my-lessons", status_code=303)
    except Exception as e:
        # Handle errors
        print(f"Error creating lesson: {e}")

        # Get modules for the dropdown (same as in GET route)
        modules = [
            {
                "id": 1,
                "title": "Introduction to Programming"
            },
            {
                "id": 2,
                "title": "Core Concepts"
            },
            {
                "id": 3,
                "title": "Advanced Topics"
            }
        ]

        return templates.TemplateResponse("lessons/create_lesson.html", {
            "request": request,
            "user": user if 'user' in locals() else None,
            "modules": modules,
            "error": str(e),
            "featured_courses": [],
            "trending_courses": []
        })
    except HTTPException:
        # User is not authenticated, redirect to login
        return RedirectResponse(url="/login", status_code=303)


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, response: Response):
    """Show the current user's profile."""
    # Try to get the current user from cookie
    try:
        user = await get_current_user_from_cookie(request, response)

        # Get user details
        user_dict = user.dict()

        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user,
            "user_details": user_dict,
            "title": "My Profile",
            "featured_courses": [],
            "trending_courses": []
        })
    except HTTPException:
        # User is not authenticated, redirect to login
        return RedirectResponse(url="/login", status_code=303)


@app.get("/settings", response_class=HTMLResponse)
async def settings(request: Request, response: Response):
    """Show the current user's settings."""
    # Try to get the current user from cookie
    try:
        user = await get_current_user_from_cookie(request, response)

        return templates.TemplateResponse("settings.html", {
            "request": request,
            "user": user,
            "title": "Account Settings",
            "featured_courses": [],
            "trending_courses": []
        })
    except HTTPException:
        # User is not authenticated, redirect to login
        return RedirectResponse(url="/login", status_code=303)
