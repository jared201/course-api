import asyncio
from datetime import datetime
from services.content import ContentService, Module, Lesson, ContentType

def test_module_lessons_direct():
    """Test that a Module object can have lessons assigned to it directly."""
    # Create a module directly (not using ContentService to avoid Redis)
    module = Module(
        id=1,
        course_id=123,
        title="Test Module",
        description="A module for testing",
        order=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    # Create a lesson directly
    lesson = Lesson(
        id=1,
        module_id=module.id,
        title="Test Lesson",
        description="A lesson for testing",
        content_type=ContentType.TEXT,
        content="This is the content of the test lesson",
        order=1,
        is_free_preview=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    # Assign the lesson to the module's lessons field
    module.lessons = [lesson]

    # Verify that the module has the lesson
    assert len(module.lessons) == 1, f"Expected 1 lesson, got {len(module.lessons)}"
    assert module.lessons[0].id == lesson.id, "Lesson ID mismatch"
    assert module.lessons[0].title == "Test Lesson", "Lesson title mismatch"

    print("Test passed: Module can have lessons assigned to it directly.")

if __name__ == "__main__":
    # No need for asyncio.run since we're not using async functions
    test_module_lessons_direct()
