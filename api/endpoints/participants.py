import csv
import os
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from bson import ObjectId
from schemas.participants import ParticipantCreate, ParticipantRead, ParticipantUpdate
from passlib.context import CryptContext
from db import db
from pydantic import EmailStr





pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




router = APIRouter()

@router.post("/", response_model=ParticipantRead)
async def create_participant(participant: ParticipantCreate):
    existing_participant = await db.participant_collection.find_one({"email": participant.email})
    if existing_participant:
        raise HTTPException(status_code=400, detail="Email already registered")

   
    participant_data = participant.dict()
 
    
    result = await db.participant_collection.insert_one(participant_data)
    participant_data["id"] = str(result.inserted_id)
  

    return ParticipantRead(**participant_data)




@router.post("/import_csv", response_model=List[ParticipantRead])
async def import_participants_from_csv():
    # Get the current file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "../../csv/data.csv")
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=400, 
            detail=f"CSV file not found at {file_path}. Please ensure data.csv exists in the api/endpoints directory."
        )
    
    new_participants = []
    
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                participant_data = {
                    "full_name": f"{row['firstName']} {row['lastName']}",
                    "email": row["email"],
                    "phone": row["phoneNumber"],
                    "team": row.get("teamName", " "),  # Provide a default value if team is missing
                }
                
                # Check if email already exists
                existing_participant = await db.participant_collection.find_one({"email": participant_data["email"]})
                if existing_participant:
                    continue  # Skip if email already exists
                
                # Insert into database
                result = await db.participant_collection.insert_one(participant_data)
                participant_data["id"] = str(result.inserted_id)
                new_participants.append(ParticipantRead(**participant_data))
                
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Could not open CSV file")
    except KeyError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"CSV file is missing required column: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while processing the CSV: {str(e)}"
        )
    
    if not new_participants:
        return []
        
    return new_participants

@router.get("/{participant_id}", response_model=ParticipantRead)
async def get_participant(participant_id: str):
    if not ObjectId.is_valid(participant_id):
        raise HTTPException(status_code=400, detail="Invalid participant ID")
    
    admin = await db.participant_collection.find_one({"_id": ObjectId(participant_id)})
    if admin:
        admin["id"] = str(admin.pop("_id"))
       
        return ParticipantRead(**admin)
    raise HTTPException(status_code=404, detail="participant not found")

@router.put("/{participant_id}", response_model=ParticipantRead)
async def update_participant(participant_id: str, participant: ParticipantUpdate):
    if not ObjectId.is_valid(participant_id):
        raise HTTPException(status_code=400, detail="Invalid participant ID")
    
    update_data = {k: v for k, v in participant.dict().items() if v is not None}
  
    
    result = await db.participant_collection.update_one(
        {"_id": ObjectId(participant_id)}, 
        {"$set": update_data}
    )
    
    updated_participant = await db.participant_collection.find_one({"_id": ObjectId(participant_id)})

    if updated_participant:
        updated_participant["id"] = str(updated_participant.pop("_id"))
      
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
