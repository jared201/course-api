from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
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
course_service = CourseService(featured_courses=featured_courses, trending_courses=trending_courses)
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
@app.get("/courses", response_class=HTMLResponse)
@app.get("/courses/ui", response_class=HTMLResponse)
async def list_courses_ui(request: Request, skip: int = 0, limit: int = 100, exclude: Optional[str] = None):
    """List all published courses with HTML UI."""
    filters = {"status": CourseStatus.PUBLISHED}
    # Handle the exclude parameter if provided and not empty
    if exclude and exclude.strip():
        filters["exclude"] = exclude
    courses = await course_service.list_courses(
        skip=skip, 
        limit=limit, 
        filters=filters
    )

    return templates.TemplateResponse("courses/list.html", {
        "request": request,
        "courses": courses,
        "featured_courses": featured_courses,
        "trending_courses": trending_courses
    })

@app.get("/courses/{course_id}/ui", response_class=HTMLResponse)
async def get_course_ui(request: Request, course_id: int):
    """Get a specific course by ID with HTML UI."""
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

    return templates.TemplateResponse("courses/detail.html", {
        "request": request,
        "course": course_with_modules,
        "featured_courses": featured_courses,
        "trending_courses": trending_courses,
        "user": None  # Default to None if no user is authenticated
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
        "completed_lessons": [],  # This would be populated from user progress
        "featured_courses": featured_courses,
        "trending_courses": trending_courses
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
        "completed_lessons": [],  # This would be populated from user progress
        "featured_courses": featured_courses,
        "trending_courses": trending_courses
    })

@app.get("/login", response_class=HTMLResponse)
async def login_ui(request: Request):
    """Render the login page."""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "featured_courses": featured_courses,
        "trending_courses": trending_courses
    })

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

    # In a real implementation, you would set the token in a cookie or session

    # Redirect to home page or dashboard
    return RedirectResponse(url="/", status_code=303)

@app.get("/register", response_class=HTMLResponse)
async def register_ui(request: Request):
    """Render the registration page."""
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
        user_data = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "password": password,
            "role": role
        }
        user = UserCreate(**user_data)
        created_user = await user_service.create_user(user.dict(exclude={"password"}))

        # In a real implementation, you would log the user in here

        # Redirect to login page
        return RedirectResponse(url="/login", status_code=303)
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
