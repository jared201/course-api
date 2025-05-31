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
async def list_courses(skip: int = 0, limit: int = 100):
    """List all published courses."""
    return await course_service.list_courses(
        skip=skip, 
        limit=limit, 
        filters={"status": CourseStatus.PUBLISHED}
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
    })

# HTML UI routes
@app.get("/courses/ui", response_class=HTMLResponse)
async def list_courses_ui(request: Request, skip: int = 0, limit: int = 100):
    """List all published courses with HTML UI."""
    courses = await course_service.list_courses(
        skip=skip, 
        limit=limit, 
        filters={"status": CourseStatus.PUBLISHED}
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
