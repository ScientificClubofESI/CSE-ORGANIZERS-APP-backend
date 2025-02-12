from fastapi import APIRouter, HTTPException
from bson import ObjectId
from db.db import SupervisorTask
from schemas.supervisortask import SupervisorTaskCreate, SupervisorTaskRead
from typing import List

router = APIRouter()

@router.post("/", response_model=SupervisorTaskRead)
async def create_supervisor_task(supervisor_task: SupervisorTaskCreate):
    supervisor_task_data = supervisor_task.dict()
    result = await SupervisorTask.insert_one(supervisor_task_data)
    return SupervisorTaskRead(**supervisor_task_data)

@router.get("/{task_id}", response_model=List[SupervisorTaskRead])
async def get_assigned_task(task_id: str):
    tasks = await SupervisorTask.find({"task_id": task_id}).to_list()
    if tasks: 
        return [SupervisorTaskRead(**task) for task in tasks]
    raise HTTPException(status_code=404, detail="No supervisor found for this task")

@router.get("/organizer/{organizer_id}", response_model=List[SupervisorTaskRead])
async def get_tasks_by_organizer(organizer_id: int):
    tasks = await SupervisorTask.find({"organizer_id": organizer_id}).to_list()
    if tasks:
        return [SupervisorTaskRead(**task) for task in tasks]
    raise HTTPException(status_code=404, detail="No supervision tasks found for this organizer")


