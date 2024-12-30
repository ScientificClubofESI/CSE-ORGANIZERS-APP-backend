from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.db.db import Event
from app.schemas.event import EventCreate, EventRead, EventUpdate
from typing import List
router = APIRouter()

@router.post("/", response_model=EventRead)
async def create_event(event: EventCreate):
    event_data = event.dict()
    result = await Event.insert_one(event_data)
    event_data["id"] = str(result.inserted_id)
    return EventRead(**event_data)

@router.get("/", response_model=List[EventRead])
async def get_all_tasks():
    events = await EventRead.find().to_list()
    if event:
        for event in events:
            event["id"] = str(event.pop("_id"))
        return [EventRead(**event) for event in events]
    raise HTTPException(status_code=404, detail="No events found")

@router.get("/{event_id}", response_model=EventRead)
async def get_event(event_id: str):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID")

    event = await Event.find_one({"_id": ObjectId(event_id)})
    if event:
        event["id"] = str(event.pop("_id"))
        return EventRead(**event)
    raise HTTPException(status_code=404, detail="Event not found")
    

@router.put("/{event_id}", response_model=EventRead)
async def update_event(event_id: str, event: EventUpdate):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID")

    update_data = {k: v for k, v in event.dict().items() if v is not None}
    result = await Event.update_one({"_id": ObjectId(event_id)}, {"$set": update_data})
    if result.modified_count == 1:
        updated_event = await Event.find_one({"_id": ObjectId(event_id)})
        updated_event["id"] = str(updated_event.pop("_id"))
        return EventRead(**updated_event)
    raise HTTPException(status_code=404, detail="Event not found")

@router.delete("/{event_id}")
async def delete_event(event_id: str):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID")

    result = await Event.delete_one({"_id": ObjectId(event_id)})
    if result.deleted_count == 1:
        return {"message": "Event deleted successfully"}
    raise HTTPException(status_code=404, detail="Event not found")