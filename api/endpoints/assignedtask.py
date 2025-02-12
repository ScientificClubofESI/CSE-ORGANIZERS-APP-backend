from fastapi import APIRouter, HTTPException
from bson import ObjectId
from db.db import AssignedTask
from schemas.assignedtask import AssignedTaskCreate, AssignedTaskRead, AssignedTaskUpdate
from typing import List

router = APIRouter()

@router.post("/", response_model=AssignedTaskRead)
async def create_assigned_task(task: AssignedTaskCreate):
    task_data = task.dict()
    result = await AssignedTask.insert_one(task_data)
    return AssignedTaskRead(**task_data)

@router.get("/", response_model=List[AssignedTaskRead])
async def get_all_tasks():
    tasks = await AssignedTask.find().to_list()
    if tasks:
        return [AssignedTaskRead(**task) for task in tasks]
    raise HTTPException(status_code=404, detail="No tasks found")

@router.get("/{task_id}", response_model=List[AssignedTaskRead])
async def get_assigned_task(task_id: str):
    tasks = await AssignedTask.find({"task_id": task_id}).to_list()
    if tasks:
        return [AssignedTaskRead(**task) for task in tasks]
    raise HTTPException(status_code=404, detail="No organizers found for this tasks")

@router.get("/organizer/{organizer_id}", response_model=List[AssignedTaskRead])
async def get_tasks_by_organizer(organizer_id: str):
    tasks = await AssignedTask.find({"organizer_id": organizer_id}).to_list()
    if tasks:
        return [AssignedTaskRead(**task) for task in tasks]
    raise HTTPException(status_code=404, detail="No assigned tasks found for this organizer")

