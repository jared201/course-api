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

### API Testing

The project includes a `test_main.http` file that can be used to test the API endpoints using tools like Visual Studio Code's REST Client extension or JetBrains HTTP Client.

To run API tests:

1. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

2. Use the HTTP requests in `test_main.http` to test the endpoints.

### Creating Test Accounts

Scripts are provided to create test accounts for development and testing purposes:

```bash
# Create student and instructor accounts
# Run with Redis (make sure Redis server is running)
python create_test_accounts.py

# Run in mock mode (without Redis)
MOCK_MODE=1 python create_test_accounts.py

# Create an admin account for testing the Redis endpoint
python create_admin_account.py
```

The create_test_accounts.py script creates:
- 5 student accounts (usernames: student1-student5)
- 5 instructor accounts (usernames: instructor1-instructor5)

The create_admin_account.py script creates:
- 1 admin account (username: admin, password: admin)

Student and instructor accounts use the password "password123" for testing purposes.

### Testing Redis Integration

A test script is provided to test the Redis integration endpoint:

```bash
# Step 1: Create an admin account (if not already created)
python create_admin_account.py

# Step 2: Start the API server (if not already running)
uvicorn main:app --reload

# Step 3: In a new terminal, run the test script
python test_redis_endpoint.py
```

This script:
1. Authenticates with admin credentials (username: admin, password: admin)
2. Calls the `/admin/courses/move-to-redis` endpoint
3. Displays the response from the server

Before running the script, make sure to:
- Create an admin account using the create_admin_account.py script
- Ensure Redis server is running and properly configured
- Start the API server using `uvicorn main:app --reload`
- Set Redis environment variables if needed (REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)

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
- `POST /admin/courses/move-to-redis`: Move all course data to Redis (requires admin role)

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

### Authentication
- `SECRET_KEY`: A secret key for JWT token generation
- `ALGORITHM`: The algorithm used for JWT (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes

### Redis Configuration
- `REDIS_HOST`: Redis server hostname or IP address
- `REDIS_PORT`: Redis server port
- `REDIS_PASSWORD`: Redis server password (if required)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
