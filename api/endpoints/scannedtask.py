from fastapi import APIRouter, HTTPException
from bson import ObjectId
from db.db import ScannedTask ,Participant
from schemas.scannedtask import ScannedTaskCreate, ScannedTaskRead, ScannedTaskUpdate
from typing import List
from schemas.participants import ParticipantRead
router = APIRouter()

@router.post("/", response_model=ScannedTaskRead)
async def create_scanned_task(scanned_task: ScannedTaskCreate):
    scanned_task_data = scanned_task.dict()
    result = await ScannedTask.insert_one(scanned_task_data)
    return ScannedTaskRead(**scanned_task_data)


@router.get("/{task_id}/unscanned", response_model=List[ParticipantRead])
async def get_unscanned_participants(task_id: str):

    unscanned_participants = await ScannedTask.find({"task_id": task_id, "scanned": False}).to_list(length=None)
    if not unscanned_participants:
        raise HTTPException(status_code=404, detail="No unscanned participants found")

    participants_with_details = []

    for scanned_task in unscanned_participants:
        participant_id = scanned_task.get("participant_qr")
        participant = await Participant.find_one({"_id": ObjectId(participant_id)})
        if participant:
            participant_data = {
                "qr_code": str(participant["qr_code"]),
                "full_name": participant["full_name"],
                "email": participant["email"],
                "phone": participant["phone"],
            }
            participants_with_details.append(ParticipantRead(**participant_data))
        else:
            continue  

    return participants_with_details

@router.get("/{task_id}/scanned", response_model=List[ParticipantRead])
async def get_scanned_participants(task_id: str):
    scanned_participants = await ScannedTask.find({"task_id": task_id, "scanned": True}).to_list()

    if not scanned_participants:
        raise HTTPException(status_code=404, detail="No scanned participants found")

    participants_with_details = []

    for scanned_task in scanned_participants:
        participant_id = scanned_task.get("participant_qr")
        participant = await Participant.find_one({"_id": ObjectId(participant_id)})
        if participant:
            participant_data = {
                "qr_code": str(participant["qr_code"]),
                "full_name": participant["full_name"],
                "email": participant["email"],
                "phone": participant["phone"],
            }
            participants_with_details.append(ParticipantRead(**participant_data))
        else:
            continue

    return participants_with_details
