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
    # Use .to_list() to fetch the results from
    print("testttt")
    tasks = await db.assigned_task_collection.find({"task_id": task_id}).to_list(length=100) 

    if tasks:
        print(tasks)
        # Initialize an empty list to store the full names of organizers and supervisors
        result = []

        for task in tasks:
            # Fetch full names from the organizer collection
            organizers = await db.organizer_collection.find({"_id": {"$in": [ObjectId(id) for id in task["organizer_id"]]}}).to_list(length=100)
            organizers_names = [organizer["full_name"] for organizer in organizers]

            # Fetch full names from the supervisor collection
            supervisors = await db.organizer_collection.find({"_id": {"$in": [ObjectId(id) for id in task["supervisor_id"]]}}).to_list(length=100)
            supervisors_names = [supervisor["full_name"] for supervisor in supervisors]

            # Create the result object with the full names instead of IDs
            result.append(AssignedTaskRead(
                task_id=task["task_id"],
                organizer_id=organizers_names,
                supervisor_id=supervisors_names
            ))

        return result

    raise HTTPException(status_code=404, detail="No organizers found for this task")


@router.get("/organizer/{organizer_id}", response_model=List[AssignedTaskRead])
async def get_tasks_by_organizer(organizer_id: str):
    tasks = await db.assigned_task_collection.find({"organizer_id": {"$in": [organizer_id]}}).to_list(length=None)
    
    if tasks:
        return [AssignedTaskRead(**task) for task in tasks]
    
    raise HTTPException(status_code=404, detail="No assigned tasks found for this organizer")
