# Star Wars API Project

A RESTful API that interacts with the Star Wars API (SWAPI) to provide information about Star Wars characters, films, and starships with voting capabilities.

## Features

- 🌟 Fetch and store Star Wars characters, films, and starships
- 🔍 Search functionality with pagination
- 🗳️ Vote for your favorite characters, films, and starships
- 📊 Comprehensive error handling
- 🧪 Full test coverage (80%+)
- 📖 Interactive API documentation

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite (with PostgreSQL support)
- **ORM**: SQLAlchemy
- **Testing**: Pytest
- **Documentation**: Swagger/OpenAPI

## Setup Instructions

### 1. Clone and Setup Environment

```bash
cd /root/uphellas
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file:

```bash
cp .env.example .env
```

### 3. Database Setup

```bash
# Run database migrations
alembic upgrade head

# Populate with SWAPI data
python scripts/populate_data.py
```

### 4. Run the Application

```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Run Tests

```bash
# Run all tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_characters.py -v
```

## API Documentation

Once the server is running, visit:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## API Endpoints

### Characters
- `GET /api/v1/characters/` - List characters with pagination
- `GET /api/v1/characters/{id}` - Get character by ID
- `GET /api/v1/characters/search?name={name}` - Search characters
- `POST /api/v1/characters/{id}/vote` - Vote for character
- `POST /api/v1/characters/sync` - Sync from SWAPI

### Films
- `GET /api/v1/films/` - List films with pagination
- `GET /api/v1/films/{id}` - Get film by ID
- `GET /api/v1/films/search?title={title}` - Search films
- `POST /api/v1/films/{id}/vote` - Vote for film
- `POST /api/v1/films/sync` - Sync from SWAPI

### Starships
- `GET /api/v1/starships/` - List starships with pagination
- `GET /api/v1/starships/{id}` - Get starship by ID
- `GET /api/v1/starships/search?name={name}` - Search starships
- `POST /api/v1/starships/{id}/vote` - Vote for starship
- `POST /api/v1/starships/sync` - Sync from SWAPI

## Project Structure

```
app/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration settings
├── database.py          # Database connection and session
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── api/                 # API routes
├── services/            # Business logic
└── utils/               # Utility functions

tests/                   # Test files
scripts/                 # Utility scripts
alembic/                 # Database migrations
```
