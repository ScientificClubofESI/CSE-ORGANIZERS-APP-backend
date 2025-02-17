from fastapi import APIRouter, HTTPException ,Query
from bson import ObjectId
import csv , os
from db.models.organizers import Organizer
from schemas.organizers import OrganizerCreate, OrganizerRead, OrganizerUpdate
from passlib.context import CryptContext
from typing import List, Optional
from db import db
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


router = APIRouter()

@router.post("/", response_model=OrganizerRead)
async def create_organizer(organizer: OrganizerCreate):
    existing_participant = await db.organizer_collection.find_one({"email": organizer.email})
    if existing_participant:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(organizer.password)
    organizer_data = organizer.dict()
    organizer_data["password"] = hashed_password
    result = await db.organizer_collection.insert_one(organizer_data)
    organizer_data["id"] = str(result.inserted_id)
    organizer_data.pop("password") 
    return OrganizerRead(**organizer_data)


@router.post("/import_csv", response_model=List[OrganizerRead])
async def import_organizers_from_csv():
    # Define file path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "../../csv/organizers.csv")

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=400, 
            detail=f"CSV file not found at {file_path}. Please ensure organizers.csv exists."
        )

    new_organizers = []

    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                organizer_data = {
                    "full_name": row["full_name"],
                    "email": row["email"],  # Ensure email is unique
                    "phone": row["phone"],
                    "status": row["status"],  # Expecting "free", "occupied", or "timeout"
                    "department": row["department"].strip().lower(),  # Convert department to lowercase
                    "is_absent": row.get("is_absent", "False").lower() == "true",  # Convert string to boolean
                    "password": row["password"],  # Will be hashed
                }

                # Check if email already exists
                existing_organizer = await db.organizer_collection.find_one({"email": organizer_data["email"]})
                if existing_organizer:
                    continue  # Skip duplicate emails
                
                # Hash the password before storing
                organizer_data["password"] = hash_password(organizer_data["password"])

                # Insert into database
                result = await db.organizer_collection.insert_one(organizer_data)
                organizer_data["id"] = str(result.inserted_id)
                organizer_data.pop("password")  # Do not expose hashed password in response
                new_organizers.append(OrganizerRead(**organizer_data))

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

    return new_organizers


@router.get("/", response_model=List[OrganizerRead])
async def get_all_organizers():
    organizers = await db.organizer_collection.find().to_list()
    if organizers:
        for organizer in organizers:
            organizer["id"] = str(organizer.pop("_id"))  
            organizer.pop("password", None)  
        return [OrganizerRead(**organizer) for organizer in organizers]
    raise HTTPException(status_code=404, detail="No organizers found")

@router.get("/{organizer_id}", response_model=OrganizerRead)
async def get_organizer(organizer_id: str):
    if not ObjectId.is_valid(organizer_id):
        raise HTTPException(status_code=400, detail="Invalid organizer ID")

    organizer = await db.organizer_collection.find_one({"_id": ObjectId(organizer_id)})
    if organizer:
        organizer["id"] = str(organizer.pop("_id"))
        return OrganizerRead(**organizer)
    raise HTTPException(status_code=404, detail="Organizer not found")

@router.put("/{organizer_id}", response_model=OrganizerRead)
async def update_organizer(organizer_id: str, organizer: OrganizerUpdate):
    if not ObjectId.is_valid(organizer_id):
        raise HTTPException(status_code=400, detail="Invalid organizer ID")

    update_data = {k: v for k, v in organizer.dict().items() if v is not None}
    result = await db.organizer_collection.update_one({"_id": ObjectId(organizer_id)}, {"$set": update_data})
    if result.modified_count == 1:
        updated_organizer = await db.organizer_collection.find_one({"_id": ObjectId(organizer_id)})
        updated_organizer["id"] = str(updated_organizer.pop("_id"))
        return OrganizerRead(**updated_organizer)
    raise HTTPException(status_code=404, detail="Organizer not found")

@router.delete("/{organizer_id}")
async def delete_organizer(organizer_id: str):
    if not ObjectId.is_valid(organizer_id):
        raise HTTPException(status_code=400, detail="Invalid organizer ID")

    result = await db.organizer_collection.delete_one({"_id": ObjectId(organizer_id)})
    if result.deleted_count == 1:
        return {"message": "Organizer deleted successfully"}
    raise HTTPException(status_code=404, detail="Organizer not found")


@router.get("/1/search", response_model=List[OrganizerRead])
async def search_organizers(
    full_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
):
    query = {}
 
    if full_name:
        query["full_name"] = full_name
    if status:
        query["status"] = status
    if department:
        query["department"] = department

    print(f"Received full_name: {full_name}, status: {status}")
    organizers = await db.organizer_collection.find(query).to_list()
    if organizers:
        for organizer in organizers:
            organizer["id"] = str(organizer.pop("_id")) 
            organizer.pop("password", None)  
        return [OrganizerRead(**organizer) for organizer in organizers]
    
    raise HTTPException(status_code=404, detail="No organizers match the search criteria")

@router.get("/1/absent", response_model=List[OrganizerRead])
async def get_absent_organizers():
    organizers = await db.organizer_collection.find({"is_absent": True}).to_list()
    if organizers:
        for organizer in organizers:
            organizer["id"] = str(organizer.pop("_id"))
            organizer.pop("password", None)  
        return [OrganizerRead(**organizer) for organizer in organizers]
    raise HTTPException(status_code=404, detail="No absent organizers found")


@router.get("/1/present", response_model=List[OrganizerRead])
async def get_present_organizers():
    organizers = await db.organizer_collection.find({"is_absent": False}).to_list()
    if organizers:
        for organizer in organizers:
            organizer["id"] = str(organizer.pop("_id"))
            organizer.pop("password", None)  
        return [OrganizerRead(**organizer) for organizer in organizers]
    raise HTTPException(status_code=404, detail="No present organizers found")

@router.get("/1/statistics")
async def get_organizer_statistics():
    total_organizers = await db.organizer_collection.count_documents({})
    present_organizers = await db.organizer_collection.count_documents({"is_absent": False})
    absent_organizers = await db.organizer_collection.count_documents({"is_absent": True})
    free_organizers = await db.organizer_collection.count_documents({"status": "free"})

    return {
        "total_organizers": total_organizers,
        "present_organizers": present_organizers,
        "absent_organizers": absent_organizers,
        "free_organizers": free_organizers
    }
