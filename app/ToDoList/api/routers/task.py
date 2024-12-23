from typing import List

from fastapi import APIRouter

from api.schemas.task import Task, TaskCreate, TaskCreateResponse

router = APIRouter()


@router.get("/tasks", response_model=List[Task])
async def list_tasks():
    return [Task(id=1, title="1つ目のTODOタスク")]


@router.post("/tasks", response_model=TaskCreateResponse)
async def create_task(task_body: TaskCreate):
    return TaskCreateResponse(id=1, **task_body.model_dump())


@router.put("/tasks/{task_id}")
async def update_task():
    pass


@router.delete("/tasks/{task_id}")
async def delete_task():
    pass
