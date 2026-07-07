from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import os

#Creating the limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["5/minute"])

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")

app = FastAPI()
app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# API Key Authentication
api_key_header = APIKeyHeader(
    name="x-api-key",
    auto_error=False
)


def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key is None:
        raise HTTPException(
            status_code=403,
            detail="API Key missing"
        )

    if api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    return api_key


todos = []
id_counter = 1


class Todo(BaseModel):
    title: str = Field(min_length=1)
    checked: bool = False
    priority: Literal["low", "medium", "high"] = "medium"


# Bonus endpoint (No authentication)
@app.get("/")
def home():
    return {
        "message": "Welcome to the Authenticated Todo API"
    }


@app.get("/todos")
def get_todos(api_key: str = Depends(verify_api_key)):
    return todos


@app.post("/todos", status_code=201)
@limiter.limit("3/minute")
async def create_todo(
    request: Request,
    todo: Todo,
    api_key: str = Depends(verify_api_key)
):
    global id_counter

    new_todo = todo.model_dump()
    new_todo["id"] = id_counter

    todos.append(new_todo)

    id_counter += 1

    return {
        "message": "Todo added successfully"
    }


@app.get("/todos/{id}")
def get_todo(
    id: int,
    api_key: str = Depends(verify_api_key)
):
    for todo in todos:
        if todo["id"] == id:
            return todo

    raise HTTPException(
        status_code=404,
        detail="Todo not found"
    )


@app.put("/todos/{id}")
def update_todo(
    id: int,
    updated_todo: Todo,
    api_key: str = Depends(verify_api_key)
):
    for todo in todos:
        if todo["id"] == id:
            todo["title"] = updated_todo.title
            todo["checked"] = updated_todo.checked
            todo["priority"] = updated_todo.priority

            return {
                "message": "Todo updated successfully"
            }

    raise HTTPException(
        status_code=404,
        detail="Todo not found"
    )


@app.delete("/todos/{id}")
def delete_todo(
    id: int,
    api_key: str = Depends(verify_api_key)
):
    for todo in todos:
        if todo["id"] == id:
            todos.remove(todo)

            return {
                "message": "Todo deleted successfully"
            }

    raise HTTPException(
        status_code=404,
        detail="Todo not found"
    )