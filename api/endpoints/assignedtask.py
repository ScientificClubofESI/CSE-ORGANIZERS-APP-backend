from fastapi import APIRouter, HTTPException
from bson import ObjectId
from db.models.assignedtask import AssignedTask
from schemas.assignedtask import AssignedTaskCreate, AssignedTaskRead, AssignedTaskUpdate
from typing import List
from db import db
from pymongo import ReturnDocument

router = APIRouter()

@router.post("/", response_model=AssignedTaskRead)
async def create_assigned_task(task: AssignedTaskCreate):
    task_data = task.dict()

    # Replace the old task with the same task_id if it exists
    updated_task = await db.assigned_task_collection.find_one_and_update(
        {"task_id": task_data["task_id"]},  # Search condition
        {"$set": task_data},  # Update the document
        upsert=True,  # Insert if not found
        return_document=ReturnDocument.AFTER  # Return the updated document
    )

    # Convert MongoDB ObjectId to string for response
    updated_task["id"] = str(updated_task["_id"])
    
    return AssignedTaskRead(**updated_task)

@router.get("/", response_model=List[AssignedTaskRead])
async def get_all_tasks():
    tasks = await db.assigned_task_collection.find().to_list()
    if tasks:
        return [AssignedTaskRead(**task) for task in tasks]
    raise HTTPException(status_code=404, detail="No tasks found")

@router.get("/{task_id}", response_model=List[AssignedTaskRead])
async def get_assigned_task(task_id: str):
    tasks = await db.assigned_task_collection.find({"task_id": task_id}).to_list()
    if tasks:
        return [AssignedTaskRead(**task) for task in tasks]
    raise HTTPException(status_code=404, detail="No organizers found for this tasks")

@router.get("/organizer/{organizer_id}", response_model=List[AssignedTaskRead])
async def get_tasks_by_organizer(organizer_id: str):
    tasks = await db.assigned_task_collection.find({"organizer_id": {"$in": [organizer_id]}}).to_list(length=None)
    
    if tasks:
        return [AssignedTaskRead(**task) for task in tasks]
    
    raise HTTPException(status_code=404, detail="No assigned tasks found for this organizer")
