import os
import sys
from pathlib import Path
from typing import List

import django
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add the parent directory to Python path to access the submodule
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todo_project.settings")
django.setup()

# Import Django models after setup
from django_modals.models import Todo
from django_modals.serializers import TodoSerializer

app = FastAPI(title="Todo API")


class TodoCreate(BaseModel):
    title: str
    description: str = ""
    completed: bool = False


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@app.get("/todos/", response_model=List[TodoResponse])
async def list_todos():
    todos = Todo.objects.all()
    return [TodoResponse.model_validate(todo) for todo in todos]


@app.post("/todos/", response_model=TodoResponse)
async def create_todo(todo: TodoCreate):
    todo_obj = Todo.objects.create(
        title=todo.title, description=todo.description, completed=todo.completed
    )
    return TodoResponse.model_validate(todo_obj)


@app.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int):
    try:
        todo = Todo.objects.get(id=todo_id)
        return TodoResponse.model_validate(todo)
    except Todo.DoesNotExist:
        raise HTTPException(status_code=404, detail="Todo not found")


@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, todo: TodoCreate):
    try:
        todo_obj = Todo.objects.get(id=todo_id)
        todo_obj.title = todo.title
        todo_obj.description = todo.description
        todo_obj.completed = todo.completed
        todo_obj.save()
        return TodoResponse.model_validate(todo_obj)
    except Todo.DoesNotExist:
        raise HTTPException(status_code=404, detail="Todo not found")


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    try:
        todo = Todo.objects.get(id=todo_id)
        todo.delete()
        return {"message": "Todo deleted successfully"}
    except Todo.DoesNotExist:
        raise HTTPException(status_code=404, detail="Todo not found")
