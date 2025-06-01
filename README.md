# Online Course Platform API

A FastAPI-based API for an online course platform that allows instructors to create courses and students to enroll in them.

## Features

- User management (students and instructors)
- Course creation and management
- Content organization (modules and lessons)
- Student enrollment
- Progress tracking
- Authentication and authorization
- Payment processing

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd CoursesAPI
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Locally

Start the development server:

```bash
uvicorn main:app --reload
```

The API will be available at http://127.0.0.1:8000.

## Testing

The project includes a `test_main.http` file that can be used to test the API endpoints using tools like Visual Studio Code's REST Client extension or JetBrains HTTP Client.

To run tests:

1. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

2. Use the HTTP requests in `test_main.http` to test the endpoints.

## API Documentation

Once the server is running, you can access the auto-generated API documentation:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

The API provides the following key endpoints:

### Authentication
- `POST /token`: Get an access token by providing username and password

### Users
- `POST /users/`: Create a new user
- `GET /users/me`: Get the current authenticated user's profile

### Courses
- `GET /courses/`: List all published courses
- `POST /courses/`: Create a new course (requires instructor role)
- `GET /courses/{course_id}`: Get a specific course by ID
- `GET /api/trending-courses`: Get a list of 5 trending courses

## Deployment

### Deploying to Heroku

1. Create a Heroku account and install the Heroku CLI:
   ```bash
   npm install -g heroku
   ```

2. Login to Heroku:
   ```bash
   heroku login
   ```

3. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```

4. Create a `Procfile` in the root directory with the following content:
   ```
   web: uvicorn main:app --host=0.0.0.0 --port=${PORT:-5000}
   ```

5. Add a runtime.txt file to specify the Python version:
   ```
   python-3.9.7
   ```

6. Commit the changes:
   ```bash
   git add .
   git commit -m "Add Heroku deployment files"
   ```

7. Push to Heroku:
   ```bash
   git push heroku main
   ```

8. Open the app:
   ```bash
   heroku open
   ```

### Deploying to Render.com

1. Create a Render.com account and log in.

2. Click on "New" and select "Web Service".

3. Connect your GitHub repository.

4. Configure the service:
   - Name: your-app-name
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

5. Click "Create Web Service".

6. Render will automatically deploy your application and provide a URL.

## Environment Variables

For production deployments, you should set the following environment variables:

- `SECRET_KEY`: A secret key for JWT token generation
- `ALGORITHM`: The algorithm used for JWT (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
