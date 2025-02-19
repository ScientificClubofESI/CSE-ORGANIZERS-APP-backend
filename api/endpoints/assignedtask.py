from fastapi import APIRouter, HTTPException
from bson import ObjectId
from db.models.assignedtask import AssignedTask
from schemas.assignedtask import AssignedTaskCreate, AssignedTaskRead, AssignedTaskUpdate
from typing import List
from db import db
from pymongo import ReturnDocument
from schemas.tasks import TaskCreate, TaskRead, TaskUpdate
from typing import List, Dict

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


@router.get("/organizer/{organizer_id}", response_model=List[Dict])
async def get_tasks_by_organizer(organizer_id: str):
    # Initialize an empty list to store all task IDs and their roles
    task_roles = {}
    
    # Étape 1 : Récupérer les tâches assignées à cet organizer_id (as regular organizer)
    assigned_tasks = await db.assigned_task_collection.find(
        {"organizer_id": {"$in": [organizer_id]}}
    ).to_list(length=None)
    
    if assigned_tasks:
        # Map task_ids to regular organizer role
        for task in assigned_tasks:
            if ObjectId.is_valid(task["task_id"]):
                task_roles[task["task_id"]] = {"is_supervisor": False}
    
    # Étape 2 : Récupérer les tâches où l'utilisateur est supervisor
    supervised_tasks = await db.assigned_task_collection.find(
        {"supervisor_id": organizer_id}
    ).to_list(length=None)
    
    if supervised_tasks:
        # Map task_ids to supervisor role
        for task in supervised_tasks:
            if ObjectId.is_valid(task["task_id"]):
                task_roles[task["task_id"]] = {"is_supervisor": True}
    
    # If no tasks found at all, raise exception
    if not task_roles:
        raise HTTPException(status_code=404, detail="No tasks found for this organizer (neither as assignee nor supervisor)")
    
    # Convert keys to ObjectId for MongoDB query
    task_ids = [ObjectId(task_id) for task_id in task_roles.keys()]
    
    # Étape 3 : Trouver toutes les tâches dans task_collection
    tasks = await db.task_collection.find({"_id": {"$in": task_ids}}).to_list(length=None)
    
    # Create enhanced task objects with role information
    enhanced_tasks = []
    for task in tasks:
        # Convert ObjectId to string for the response
        task_id_str = str(task.pop("_id"))
        task["id"] = task_id_str
        
        # Create a TaskRead object with additional is_supervisor field
        task_data = dict(TaskRead(**task).dict())
        # Add the is_supervisor information
        task_data.update(task_roles[task_id_str])
        enhanced_tasks.append(task_data)
    
    return enhanced_tasks