from fastapi import APIRouter, HTTPException
from bson import ObjectId
from db.models.scannedtask import ScannedTask 
from db.models.participants  import  Participant
from schemas.scannedtask import ScannedTaskCreate, ScannedTaskRead, ScannedTaskUpdate
from typing import List
from schemas.participants import ParticipantRead
from db import db

router = APIRouter()

@router.post("/", response_model=ScannedTaskRead)
async def create_scanned_task(scanned_task: ScannedTaskCreate):
    scanned_task_data = scanned_task.dict()
    result = await db.scanned_task_collection.insert_one(scanned_task_data)
    return ScannedTaskRead(**scanned_task_data)

@router.put("/", response_model=ScannedTaskRead)
async def update_scanned_status(scanned_task_update: ScannedTaskUpdate):
    # Extract fields from the input
    task_id = scanned_task_update.task_id
    participant_qr = scanned_task_update.participant_qr
    scanned_status = scanned_task_update.scanned

    # Define the filter to find the specific task and participant
    filter_query = {
        "task_id": task_id,
        "participant_qr": participant_qr
    }

    # Define the update operation
    update_data = {
        "$set": {
            "scanned": scanned_status
        }
    }

    # Perform the update operation
    result = await db.scanned_task_collection.update_one(filter_query, update_data)

    # Check if the task was found and updated
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task or participant not found")

    # Fetch the updated task to return it
    updated_task = await db.scanned_task_collection.find_one(filter_query)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found after update")

    return ScannedTaskRead(**updated_task)



@router.get("/{task_id}", response_model=List[dict])  
async def get_all_participants_with_scan_status(task_id: str):
    # Retrieve all participants
    participants = await db.participant_collection.find().to_list(length=None)

    if not participants:
        raise HTTPException(status_code=404, detail="No participants found")

    participants_with_status = []

    for participant in participants:
        participant_id = str(participant["_id"])

        # Check if the participant exists in the scanned_task_collection
        scanned_task = await db.scanned_task_collection.find_one({
            "task_id": task_id,
            "participant_qr": participant_id
        })

        participant_data = {
            "task_id": task_id,
            "participant_qr": participant_id,
            "full_name": participant["full_name"],
            "email": participant["email"],
            "phone": participant["phone"],
            "scanned": True if scanned_task else False
        }

        participants_with_status.append(participant_data)

    return participants_with_status


@router.get("/{task_id}/scanned", response_model=List[ParticipantRead])
async def get_scanned_participants(task_id: str):
    scanned_participants = await db.scanned_task_collection.find({"task_id": task_id, "scanned": True}).to_list()

    if not scanned_participants:
        raise HTTPException(status_code=404, detail="No scanned participants found")

    participants_with_details = []

    for scanned_task in scanned_participants:
        participant_id = scanned_task.get("participant_qr")
        participant = await db.participant_collection.find_one({"_id": ObjectId(participant_id)})
        if participant:
            participant_data = {
                "id": str(participant["id"]),
                "full_name": participant["full_name"],
                "email": participant["email"],
                "phone": participant["phone"],
            }
            participants_with_details.append(ParticipantRead(**participant_data))
        else:
            continue

    return participants_with_details

