from ninja import NinjaAPI, Schema
from typing import List, Optional
from django.shortcuts import get_object_or_404
from .models import Task

api = NinjaAPI()

# 定义Schema
class TaskSchema(Schema):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: str
    updated_at: str

class TaskCreateSchema(Schema):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskUpdateSchema(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# API路由
@api.get("/tasks", response=List[TaskSchema])
def list_tasks(request):
    tasks = Task.objects.all()
    return tasks

@api.get("/tasks/{task_id}", response=TaskSchema)
def get_task(request, task_id: int):
    task = get_object_or_404(Task, id=task_id)
    return task

@api.post("/tasks", response=TaskSchema)
def create_task(request, task: TaskCreateSchema):
    task_obj = Task.objects.create(**task.dict())
    return task_obj

@api.put("/tasks/{task_id}", response=TaskSchema)
def update_task(request, task_id: int, data: TaskUpdateSchema):
    task = get_object_or_404(Task, id=task_id)
    
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(task, attr, value)
    
    task.save()
    return task

@api.delete("/tasks/{task_id}")
def delete_task(request, task_id: int):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return {"success": True}