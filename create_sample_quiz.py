from services.content import ContentService, ContentType
import asyncio
import json

async def create_sample_quiz():
    content_service = ContentService()
    
    # Create a sample quiz
    quiz_data = {
        "title": "Python Basics Quiz",
        "description": "Test your knowledge of Python basics",
        "questions": [
            {
                "text": "What is Python?",
                "type": "multiple_choice",
                "options": [
                    "A snake",
                    "A programming language",
                    "A web framework",
                    "A database"
                ],
                "correct_answer": 2  # Index of the correct option (0-based)
            },
            {
                "text": "Which of the following are valid Python data types? (Select all that apply)",
                "type": "checkbox",
                "options": [
                    "Integer",
                    "Float",
                    "String",
                    "Boolean"
                ],
                "correct_answers": [1, 2, 3, 4]  # Indices of correct options (1-based for form submission)
            },
            {
                "text": "Explain the difference between a list and a tuple in Python.",
                "type": "text",
                "sample_answer": "Lists are mutable (can be changed) while tuples are immutable (cannot be changed after creation)."
            }
        ]
    }
    
    # Convert quiz data to JSON string
    quiz_content = json.dumps(quiz_data)
    
    # Create a lesson with quiz content
    lesson_data = {
        "module_id": 1,  # Replace with an actual module ID from your system
        "title": "Python Basics Quiz",
        "description": "Test your knowledge of Python basics",
        "content_type": ContentType.QUIZ,
        "content": quiz_content,
        "order": 1,
        "is_free_preview": True
    }
    
    # Create the lesson
    lesson = await content_service.create_lesson(lesson_data)
    
    if lesson:
        print(f"Sample quiz created successfully with ID: {lesson.id}")
        print(f"Module ID: {lesson.module_id}")
        print(f"Content Type: {lesson.content_type}")
    else:
        print("Failed to create sample quiz")

if __name__ == "__main__":
    asyncio.run(create_sample_quiz())