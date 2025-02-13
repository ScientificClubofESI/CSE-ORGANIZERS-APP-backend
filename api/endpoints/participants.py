
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from schemas.participants import ParticipantCreate, ParticipantRead, ParticipantUpdate
from passlib.context import CryptContext
from db import db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def hash_password(password: str) -> str:
    return pwd_context.hash(password)

router = APIRouter()

@router.post("/", response_model=ParticipantRead)
async def create_participant(participant: ParticipantCreate):
    existing_participant = await db.participant_collection.find_one({"email": participant.email})
    if existing_participant:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(participant.password)
    participant_data = participant.dict()
    participant_data["password"] = hashed_password
    
    result = await db.participant_collection.insert_one(participant_data)
    participant_data["id"] = str(result.inserted_id)
    participant_data.pop("password") 

    return ParticipantRead(**participant_data)

@router.get("/{participant_id}", response_model=ParticipantRead)
async def get_participant(participant_id: str):
    if not ObjectId.is_valid(participant_id):
        raise HTTPException(status_code=400, detail="Invalid participant ID")
    
    admin = await db.participant_collection.find_one({"_id": ObjectId(participant_id)})
    if admin:
        admin["id"] = str(admin.pop("_id"))
        admin.pop("password", None)
        return ParticipantRead(**admin)
    raise HTTPException(status_code=404, detail="participant not found")

@router.put("/{participant_id}", response_model=ParticipantRead)
async def update_participant(participant_id: str, participant: ParticipantUpdate):
    if not ObjectId.is_valid(participant_id):
        raise HTTPException(status_code=400, detail="Invalid participant ID")
    
    update_data = {k: v for k, v in participant.dict().items() if v is not None}
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])
    
    result = await db.participant_collection.update_one(
        {"_id": ObjectId(participant_id)}, 
        {"$set": update_data}
    )
    
    updated_participant = await db.participant_collection.find_one({"_id": ObjectId(participant_id)})

    if updated_participant:
        updated_participant["id"] = str(updated_participant.pop("_id"))
        updated_participant.pop("password", None)
        return ParticipantRead(**updated_participant)
    raise HTTPException(status_code=404, detail="participant not found")

@router.delete("/{participant_id}")
async def delete_participant(participant_id: str):
    if not ObjectId.is_valid(participant_id):
        raise HTTPException(status_code=400, detail="Invalid participant ID")
    
    result = await db.participant_collection.delete_one({"_id": ObjectId(participant_id)})
    if result.deleted_count == 1:
        return {"message": "participant deleted successfully"}
    raise HTTPException(status_code=404, detail="Participant not found")
