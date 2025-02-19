from fastapi import APIRouter, HTTPException , Query
from bson import ObjectId
from db.models.tasks import Task
from schemas.tasks import TaskCreate, TaskRead, TaskUpdate
from typing import List
from datetime import datetime
from db import db

router = APIRouter()

@router.post("/", response_model=TaskRead)
async def create_task(task: TaskCreate):
    task_data = task.dict()
    result = await db.task_collection.insert_one(task_data)
    task_data["id"] = str(result.inserted_id)
    return TaskRead(**task_data)

@router.get("/", response_model=List[TaskRead])
async def get_all_tasks():
    tasks = await db.task_collection.find().to_list()
    if tasks:
        for task in tasks:
            task["id"] = str(task.pop("_id")) 
        return [TaskRead(**task) for task in tasks]
    raise HTTPException(status_code=404, detail="No tasks found")

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: str):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")

    task = await db.task_collection.find_one({"_id": ObjectId(task_id)})
    if task:
        task["id"] = str(task.pop("_id"))
        return TaskRead(**task)
    raise HTTPException(status_code=404, detail="Task not found")

@router.put("/{task_id}", response_model=TaskRead)
async def update_task(task_id: str, task: TaskUpdate):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")

    update_data = {k: v for k, v in task.dict().items() if v is not None}
    result = await db.task_collection.update_one({"_id": ObjectId(task_id)}, {"$set": update_data})

    if result.modified_count == 1:
        updated_task = await db.task_collection.find_one({"_id": ObjectId(task_id)})
        updated_task["id"] = str(updated_task.pop("_id"))
        return TaskRead(**updated_task)

    raise HTTPException(status_code=404, detail="Task not found")



@router.delete("/{task_id}")
async def delete_task(task_id: str):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")

    # Delete the main task
    task_result = await db.task_collection.delete_one({"_id": ObjectId(task_id)})

    # Delete any assigned tasks related to this task
    assigned_task_result = await db.assigned_task_collection.delete_many({"task_id": task_id})

    if task_result.deleted_count == 1:
        return {
            "message": "Task deleted successfully",
        }

    raise HTTPException(status_code=404, detail="Task not found")


@router.get("/1/search", response_model=List[TaskRead])
async def search_tasks(
    name: str = Query(None, description="Search by task name"),
    start_time: datetime = Query(None, description="Start time of the task"),
    end_time: datetime = Query(None, description="End time of the task"),
    day: datetime = Query(None, description="Specific day of the task")
):
    query = {}

    if name:
        query["name"] = name  
    if start_time:
        query["start_time"] = {"$gte": start_time}
    if end_time:
        query["end_time"] = {"$lte": end_time}
    if day:
        query["day"] = day  

    tasks = await db.task_collection.find(query).to_list()
    if tasks:
        for task in tasks:
            task["id"] = str(task.pop("_id")) 
        return [TaskRead(**task) for task in tasks]

    raise HTTPException(status_code=404, detail="No tasks found matching the criteria")

@router.get("/1/unfinished", response_model=List[TaskRead])
async def get_unfinished_tasks():
    tasks = await db.task_collection.find({"is_complete": False}).to_list()
    if tasks:
        for task in tasks:
            task["id"] = str(task.pop("_id"))  
        return [TaskRead(**task) for task in tasks]

    raise HTTPException(status_code=404, detail="No unfinished tasks found")

from datetime import datetime

@router.get("/1/late", response_model=List[TaskRead])
async def get_late_tasks():
    current_time = datetime.utcnow()
    tasks = await db.task_collection.find({
        "is_complete": False,
        "end_time": {"$lt": current_time}
    }).to_list()

    if tasks:
        for task in tasks:
            task["id"] = str(task.pop("_id")) 
        return [TaskRead(**task) for task in tasks]

    raise HTTPException(status_code=404, detail="No late tasks found")

@router.get("/1/statistics")
async def get_task_statistics():
    total_tasks = await db.task_collection.count_documents({})
    finished_tasks = await db.task_collection.count_documents({"is_complete": True})
    late_tasks = await db.task_collection.count_documents({
        "is_complete": False,
        "end_time": {"$lt": datetime.utcnow()}
    })
    progress = (finished_tasks / total_tasks) * 100 if total_tasks > 0 else 0

    return {
        "total_tasks": total_tasks,
        "finished_tasks": finished_tasks,
        "late_tasks": late_tasks,
        "progress": round(progress, 2)  
    }
