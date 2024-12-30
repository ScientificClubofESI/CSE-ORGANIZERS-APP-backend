import qrcode
import base64
from io import BytesIO
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.db.db import Participant
from app.schemas.participants import ParticipantCreate, ParticipantRead, ParticipantUpdate
from passlib.context import CryptContext
from typing import Optional
from typing import List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# QR code generation function (Base64 encoded string)
def generate_qr_code(data: str) -> str:
    qr = qrcode.make(data)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    qr_code_string = base64.b64encode(buffered.getvalue()).decode("utf-8")  # Encode as base64 string
    return qr_code_string


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

router = APIRouter()

@router.post("/", response_model=ParticipantRead)
async def create_participant(participant: ParticipantCreate):
    hashed_password = hash_password(participant.password)
    participant_data = participant.dict()
    participant_data["password"] = hashed_password
    qr_code_image = generate_qr_code(participant_data["full_name"])
    participant_data["qr_code"] = qr_code_image
    result = await Participant.insert_one(participant_data)
    participant_data["qr_code"] = str(result.inserted_id)  
    participant_data.pop("password") 

    return ParticipantRead(**participant_data)

@router.get("/{qr_code}", response_model=ParticipantRead)
async def get_participant(qr_code: str):
    participant = await Participant.find_one({"qr_code": qr_code})
    if participant:
        participant["qr_code"] = qr_code  
        return ParticipantRead(**participant)
    raise HTTPException(status_code=404, detail="Participant not found")

@router.put("/{qr_code}", response_model=ParticipantRead)
async def update_participant(qr_code: str, participant: ParticipantUpdate):
    update_data = {k: v for k, v in participant.dict().items() if v is not None}
    result = await Participant.update_one({"qr_code": qr_code}, {"$set": update_data})
    if result.modified_count == 1:
        updated_participant = await Participant.find_one({"qr_code": qr_code})
        updated_participant["qr_code"] = qr_code
        return ParticipantRead(**updated_participant)
    raise HTTPException(status_code=404, detail="Participant not found")

@router.delete("/{qr_code}")
async def delete_participant(qr_code: str):
    result = await Participant.delete_one({"qr_code": qr_code})
    if result.deleted_count == 1:
        return {"message": "Participant deleted successfully"}
    raise HTTPException(status_code=404, detail="Participant not found")
