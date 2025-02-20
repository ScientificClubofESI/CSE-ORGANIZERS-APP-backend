from fastapi import APIRouter, HTTPException , Query
from bson import ObjectId
from db.models.tasks import Task
from schemas.tasks import TaskCreate, TaskRead, TaskUpdate
from typing import List
from datetime import date, datetime , time
from db import db
import os
import csv

router = APIRouter()

@router.post("/", response_model=TaskRead)
async def create_task(task: TaskCreate):
    task_data = task.dict()
    result = await db.task_collection.insert_one(task_data)
    task_data["id"] = str(result.inserted_id)
    return TaskRead(**task_data)

@router.get("/", response_model=List[TaskRead])
async def get_all_tasks():
    tasks = await db.task_collection.find().to_list(length=None)
    print("Raw tasks from DB:", tasks)  # Debug print
    if tasks:
        transformed_tasks = []
        for task in tasks:
            task["id"] = str(task["_id"])
            del task["_id"]
            transformed_tasks.append(task)
        print("Transformed tasks:", transformed_tasks)  # Debug print
        return [TaskRead(**task) for task in transformed_tasks]
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

    # Filter out None values from the update data
    update_data = {k: v for k, v in task.dict().items() if v is not None}

    # If no valid fields are provided for update, return the existing task
    if not update_data:
        existing_task = await db.task_collection.find_one({"_id": ObjectId(task_id)})
        if existing_task:
            existing_task["id"] = str(existing_task.pop("_id"))
            return TaskRead(**existing_task)
        else:
            raise HTTPException(status_code=404, detail="Task not found")

    # Perform the update if there are valid fields
    result = await db.task_collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": update_data}
    )

    # Return the updated task
    if result.modified_count == 1:
        updated_task = await db.task_collection.find_one({"_id": ObjectId(task_id)})
        updated_task["id"] = str(updated_task.pop("_id"))
        return TaskRead(**updated_task)

    # If the task was not found, raise a 404 error
    raise HTTPException(status_code=404, detail="Task not found")



@router.post("/import_csv", response_model=List[TaskRead])
async def import_tasks_from_csv():
    # Define file path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "../../csv/day3.csv")

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=400, 
            detail=f"CSV file not found at {file_path}. Please ensure tasks.csv exists."
        )

    new_tasks = []
    task_ids = []  # To store IDs of inserted tasks

    # Supervisor and organizer ID
    supervisor_id = "67b2d9a965c4c7c2d7c0b6e1"
    organizer_id = "67b2d9a965c4c7c2d7c0b6e1"

    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Parse day (assuming DAY is an integer representing the day of the month)
                # Map DAY = 1 to 20/02/2025
                day = date(2025, 2, 22) 

                # Parse start_time
                start_time = datetime.strptime(row["start_time"], "%H:%M").time()

                # Parse end_time (default to start_time if not available or malformed)
              
               

                # Combine date and time into datetime objects
                start_datetime = datetime.combine(day, start_time)
                end_datetime = datetime.combine(day, start_time)
                day_datetime = datetime.combine(day, time.min)  # time.min is 00:00:00

                # Handle is_check_in (default to False if empty)
                is_check_in = (
                    row.get("is_check_in", "False").lower() == "true"
                    if row.get("is_check_in", "").strip()
                    else False
                )

                # Create task data
                task_data = {
                    "name": row["name"],
                    "start_time": start_datetime,
                    "end_time": end_datetime,
                    "day": day_datetime,
                    "location": row["location"].replace("\n", " ").strip(),  # Handle multi-line values
                    "description": row["description"].replace("\n", " ").strip(),  # Handle multi-line values
                    "is_complete": False,  # Default to False
                    "is_check_in": is_check_in,  # Use the parsed or default value
                }

                # Insert into task_collection
                result = await db.task_collection.insert_one(task_data)
                task_id = str(result.inserted_id)
                task_data["id"] = task_id
                task_ids.append(task_id)  # Store the task ID

                # Append to new_tasks
                new_tasks.append(TaskRead(**task_data))

        # Assign tasks to supervisor and organizer
        for task_id in task_ids:
            assigned_task_data = {
                "task_id": task_id,
                "organizer_id": [organizer_id],  # List of organizer IDs
                "supervisor_id": [supervisor_id],  # List of supervisor IDs
            }

            # Insert into assigned_task_collection
            await db.assigned_task_collection.insert_one(assigned_task_data)

    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Could not open CSV file")
    except KeyError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"CSV file is missing required column: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid data format in CSV file: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while processing the CSV: {str(e)}"
        )

    return new_tasks

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
