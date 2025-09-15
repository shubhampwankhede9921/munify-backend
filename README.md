# Blog API with FastAPI

A simple blog API built with FastAPI and MySQL.

## Features

- User management (CRUD operations)
- Post management (CRUD operations)
- Comment system
- MySQL database integration
- RESTful API endpoints
- Automatic API documentation

## Project Structure

```
blog-project/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py          # API router configuration
│   │       └── endpoints/      # API endpoints
│   │           ├── __init__.py
│   │           ├── posts.py    # Post-related endpoints
│   │           ├── users.py    # User-related endpoints
│   │           └── comments.py # Comment-related endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Application configuration
│   │   └── database.py         # Database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User SQLAlchemy model
│   │   ├── post.py             # Post SQLAlchemy model
│   │   └── comment.py          # Comment SQLAlchemy model
│   └── schemas/
│       ├── __init__.py
│       ├── user.py             # User Pydantic schemas
│       ├── post.py             # Post Pydantic schemas
│       └── comment.py          # Comment Pydantic schemas
├── requirements.txt            # Python dependencies
├── .env                       # Environment variables
├── database_init.py           # Database initialization script
├── run.py                     # Application runner
└── README.md                  # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Setup

Make sure MySQL is running on your system with the following credentials:
- Host: 127.0.0.1
- Port: 3306
- Username: root
- Password: root

Run the database initialization script:

```bash
python database_init.py
```

This will create the `blog_db` database and all necessary tables.

### 3. Run the Application

```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:

- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## API Endpoints

### Users
- `GET /api/v1/users/` - Get all users
- `GET /api/v1/users/{user_id}` - Get user by ID
- `POST /api/v1/users/` - Create new user
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Posts
- `GET /api/v1/posts/` - Get all posts (with status filter)
- `GET /api/v1/posts/{post_id}` - Get post by ID
- `POST /api/v1/posts/` - Create new post
- `PUT /api/v1/posts/{post_id}` - Update post
- `DELETE /api/v1/posts/{post_id}` - Delete post

### Comments
- `GET /api/v1/comments/` - Get all comments (with status filter)
- `GET /api/v1/comments/post/{post_id}` - Get comments for a post
- `GET /api/v1/comments/{comment_id}` - Get comment by ID
- `POST /api/v1/comments/` - Create new comment
- `PUT /api/v1/comments/{comment_id}` - Update comment
- `DELETE /api/v1/comments/{comment_id}` - Delete comment

## Environment Variables

You can customize the application by modifying the `.env` file:

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=blog_db
PROJECT_NAME=Blog API
VERSION=1.0.0
API_V1_STR=/api/v1
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Development

The application uses:
- **FastAPI** for the web framework
- **SQLAlchemy** for ORM
- **PyMySQL** for MySQL database connection
- **Pydantic** for data validation
- **Passlib** for password hashing
- **Uvicorn** as the ASGI server

## Next Steps

To extend this blog API, you could add:
- Authentication and authorization (JWT tokens)
- File upload for post images
- Categories and tags for posts
- Search functionality
- Rate limiting
- Email notifications
- Admin panel
