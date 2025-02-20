import csv
import json
import os
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from bson import ObjectId
from schemas.participants import ParticipantCreate, ParticipantRead, ParticipantUpdate
from passlib.context import CryptContext # type: ignore
from db import db
from starlette.responses import FileResponse
from pathlib import Path
import qrcode





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


@router.post("/export_csv")
async def export_participants():
    """Exports participants to a CSV file and returns the download link"""

    # Define file paths relative to the project
    current_dir = Path(__file__).resolve().parent
    csv_path = current_dir / "../../csv/participants.csv"
    qr_codes_dir = current_dir / "../../csv/qr_codes"

    # Ensure QR codes directory exists
    qr_codes_dir.mkdir(parents=True, exist_ok=True)

    # Fetch all participants from MongoDB
    participants = await db.participant_collection.find({}).to_list(length=None)

    if not participants:
        raise HTTPException(status_code=404, detail="No participants found")

    # Write participants to CSV
    with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["full_name", "qr_code"])

        for participant in participants:
            full_name = participant.get("full_name", "Unknown")
            participant_id = str(participant["_id"])
            qr_code_path = qr_codes_dir / f"{full_name}.png"

               # Generate QR Code with no border
            qr = qrcode.QRCode(
                version=1, 
                error_correction=qrcode.constants.ERROR_CORRECT_L, 
                box_size=10, 
                border=1  # <---- No white border
            )
            qr.add_data(participant_id)
            qr.make(fit=True)
            img = qr.make_image(fill="black", back_color="white")  # Generates the image

            # Save QR Code
            img.save(qr_code_path)

            # Write relative QR code path in CSV
            relative_qr_path = os.path.relpath(qr_code_path, current_dir)
            writer.writerow([full_name, relative_qr_path])

    print(f"✅ CSV exported successfully: {csv_path}")

    return FileResponse(csv_path, filename="participants.csv", media_type="text/csv")

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


@router.get("/export_participants_ids")
async def export_participants_ids():
    """
    Récupère les IDs de tous les participants existants dans la base de données
    et les enregistre dans un fichier participants_ids.txt sous la forme ["id1", "id2", ...].
    """
    try:
        # Récupérer tous les participants et extraire leurs IDs
        participants_cursor = db.participant_collection.find({}, {"_id": 1})  # Ne récupérer que les IDs
        participant_ids = [str(participant["_id"]) async for participant in participants_cursor]

        if not participant_ids:
            raise HTTPException(status_code=404, detail="Aucun participant trouvé dans la base de données.")
        
        # Sauvegarder les IDs dans un fichier .txt
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ids_file_path = os.path.join(current_dir, "participants_ids.txt")

        with open(ids_file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(json.dumps(participant_ids))  # Écriture sous forme de liste JSON

        return {"message": "IDs des participants exportés avec succès.", "file_path": ids_file_path}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'export des IDs : {str(e)}")



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
