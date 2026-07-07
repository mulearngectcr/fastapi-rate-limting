import os
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY is not set. Add it to your .env file.")

app = FastAPI(title="Todo CRUD API")

ALLOWED_PRIORITIES = ["low", "medium", "high"]


limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: Optional[str] = Security(api_key_header)):
    if api_key is None:
        raise HTTPException(status_code=403, detail="API key header missing")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key


class Todo(BaseModel):
    """Full todo, including server-assigned id. Used for responses."""
    id: int
    title: str
    checked: bool = False
    priority: str = "medium"


class TodoCreate(BaseModel):
    """Request body for POST /todos. No id -- the server assigns it."""
    title: str = Field(..., min_length=3, description="At least 3 characters")
    checked: bool = False
    priority: str = "medium"


class TodoUpdate(BaseModel):
    """Request body for PUT /todos/{id}."""
    title: str = Field(..., min_length=3, description="At least 3 characters")
    checked: bool = False
    priority: str = "medium"


todos: List[Todo] = []


def find_todo(todo_id: int) -> Optional[Todo]:
    for todo in todos:
        if todo.id == todo_id:
            return todo
    return None


def validate_priority(priority: str):
    """Business-rule validation: 400 for a bad priority value (not 422)."""
    if priority not in ALLOWED_PRIORITIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority '{priority}'. Allowed values: {ALLOWED_PRIORITIES}",
        )



@app.exception_handler(RequestValidationError)
async def custom_validation_handler(request: Request, exc: RequestValidationError):
    """
    Turns Pydantic's default (fairly cryptic) 422 error list into a
    simpler, human-readable message per field.
    """
    messages = []
    for error in exc.errors():
        field = error["loc"][-1]
        messages.append(f"'{field}': {error['msg']}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation failed", "errors": messages},
    )


@app.get("/todos", response_model=List[Todo])
def get_todos(api_key: str = Depends(verify_api_key)):
    return todos


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int, api_key: str = Depends(verify_api_key)):
    todo = find_todo(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return todo


@app.post("/todos", response_model=Todo, status_code=201)
@limiter.limit("3/minute")
def create_todo(
    request: Request, 
    todo_in: TodoCreate,
    api_key: str = Depends(verify_api_key),
):
    validate_priority(todo_in.priority)
    new_id = max((todo.id for todo in todos), default=0) + 1
    new_todo = Todo(id=new_id, **todo_in.dict())
    todos.append(new_todo)
    return new_todo


@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo_in: TodoUpdate, api_key: str = Depends(verify_api_key)):
    todo = find_todo(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")

    validate_priority(todo_in.priority)
    todo.title = todo_in.title
    todo.checked = todo_in.checked
    todo.priority = todo_in.priority
    return todo


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, api_key: str = Depends(verify_api_key)):
    todo = find_todo(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    todos.remove(todo)
    return None


@app.patch("/todos/{todo_id}/complete", response_model=Todo)
def complete_todo(todo_id: int, api_key: str = Depends(verify_api_key)):
    todo = find_todo(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    todo.checked = True
    return todo
