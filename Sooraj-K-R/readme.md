# FastAPI Todo API — Rate Limiting Implementation

## Author
**Sooraj K R**

## Overview
This is an enhanced version of the FastAPI Todo API with **rate limiting**, **API key authentication**, **Pydantic validation**, and **custom error handling** built on top of the starter template.

## Changes Made (vs. Starter Code)

### 1. Rate Limiting (SlowAPI)
- Integrated **SlowAPI** (`slowapi`) to enforce request rate limits.
- **Global default limit**: 10 requests per minute across all endpoints.
- **Stricter limit on `POST /todos`**: 3 requests per minute to prevent spam creation.
- Added `SlowAPIMiddleware` and a custom `RateLimitExceeded` exception handler.

### 2. API Key Authentication
- API key is loaded securely from a `.env` file using `python-dotenv`.
- Authentication is enforced via the `X-API-Key` header on all CRUD endpoints.
- Separate error messages for missing key (403) vs. invalid key (401).
- Root endpoint (`GET /`) is kept public with no authentication required.

### 3. Pydantic Models & Validation
- Defined separate Pydantic models for create (`ToDoCreate`) and update (`ToDoUpdate`) operations with `Field` constraints (e.g., `min_length=3` on title).
- A dedicated `ToDoItem` model is used for the stored data, which includes the auto-generated `id`.
- Priority values are validated against an allowed list: `["low", "medium", "high"]`.

### 4. Custom Error Handling
- Custom `RequestValidationError` handler returns structured 422 responses with human-readable error messages.
- Priority validation returns clear 400 errors with allowed values listed.

### 5. Additional Endpoints
- `PATCH /todos/{id}/complete` — Mark a specific todo as completed.

### 6. Filtering Support
- `GET /todos` supports optional query parameters:
  - `?priority=low|medium|high` — Filter by priority level.
  - `?checked=true|false` — Filter by completion status.

## Tech Stack
| Component       | Technology          |
|-----------------|---------------------|
| Framework       | FastAPI             |
| Rate Limiting   | SlowAPI             |
| Validation      | Pydantic            |
| Auth            | API Key (Header)    |
| Env Management  | python-dotenv       |
| Server          | Uvicorn             |

## Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file
echo 'API_KEY="your-secret-key"' > .env

# Run the server
uvicorn main:app --reload
```

## API Endpoints

| Method   | Endpoint                | Auth | Rate Limit   | Description              |
|----------|-------------------------|------|--------------|--------------------------|
| `GET`    | `/`                     | No   | Default      | Welcome message          |
| `POST`   | `/todos`                | Yes  | 3/minute     | Create a new todo        |
| `GET`    | `/todos`                | Yes  | Default      | List all todos (filterable) |
| `GET`    | `/todos/{id}`           | Yes  | Default      | Get a single todo        |
| `PUT`    | `/todos/{id}`           | Yes  | Default      | Update a todo            |
| `DELETE` | `/todos/{id}`           | Yes  | Default      | Delete a todo            |
| `PATCH`  | `/todos/{id}/complete`  | Yes  | Default      | Mark todo as completed   |

## Environment Variables

| Variable  | Description                    |
|-----------|--------------------------------|
| `API_KEY` | Secret key for API authentication |

> **Note:** The `.env` file is excluded from version control via `.gitignore`.
