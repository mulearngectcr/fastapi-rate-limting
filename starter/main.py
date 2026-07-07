"""
This authentication implementation is intentionally kept simple to help you understand the basic concepts.
In real-world applications, developers typically use more robust authentication methods such as JWT tokens,
database-stored API keys, OAuth2, or session-based authentication systems.
"""
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

API_KEY = os.getenv("API_KEY")
api_key_scheme = APIKeyHeader(name="X-API-Key")

todos = []
id_counter = 1


class Todo(BaseModel):
    title: str = Field(min_length=1)
    checked: bool = False
    priority: Literal["low", "medium", "high"] = "medium"


def authenticate(api_key: str = Security(api_key_scheme)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )


@app.get("/todos", dependencies=[Depends(authenticate)])
def get_todos():
    return todos


@app.post("/todos", status_code=201, dependencies=[Depends(authenticate)])
def create_todo(todo: Todo):
    global id_counter
    new_todo = todo.model_dump()
    new_todo["id"] = id_counter
    todos.append(new_todo)
    id_counter += 1
    return {
        "message": "Todo added successfully"
    }


@app.get("/todos/{id}", dependencies=[Depends(authenticate)])
def get_todo(id: int):
    for todo in todos:
        if todo["id"] == id:
            return todo
    raise HTTPException(
        status_code=404,
        detail="Todo not found"
    )


@app.put("/todos/{id}", dependencies=[Depends(authenticate)])
def update_todo(id: int, updated_todo: Todo):
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


@app.delete("/todos/{id}", dependencies=[Depends(authenticate)])
def delete_todo(id: int):
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
