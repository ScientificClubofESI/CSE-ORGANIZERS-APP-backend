from fastapi import APIRouter, HTTPException ,Query
from bson import ObjectId
from app.db.db import Organizer
from app.schemas.organizers import OrganizerCreate, OrganizerRead, OrganizerUpdate
from passlib.context import CryptContext
from typing import List, Optional
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


router = APIRouter()

@router.post("/", response_model=OrganizerRead)
async def create_organizer(organizer: OrganizerCreate):
    hashed_password = hash_password(organizer.password)
    organizer_data = organizer.dict()
    organizer_data["password"] = hashed_password
    result = await Organizer.insert_one(organizer_data)
    organizer_data["id"] = str(result.inserted_id)
    organizer_data.pop("password") 
    return OrganizerRead(**organizer_data)

@router.get("/", response_model=List[OrganizerRead])
async def get_all_organizers():
    organizers = await Organizer.find().to_list()
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

    organizer = await Organizer.find_one({"_id": ObjectId(organizer_id)})
    if organizer:
        organizer["id"] = str(organizer.pop("_id"))
        return OrganizerRead(**organizer)
    raise HTTPException(status_code=404, detail="Organizer not found")

@router.put("/{organizer_id}", response_model=OrganizerRead)
async def update_organizer(organizer_id: str, organizer: OrganizerUpdate):
    if not ObjectId.is_valid(organizer_id):
        raise HTTPException(status_code=400, detail="Invalid organizer ID")

    update_data = {k: v for k, v in organizer.dict().items() if v is not None}
    result = await Organizer.update_one({"_id": ObjectId(organizer_id)}, {"$set": update_data})
    if result.modified_count == 1:
        updated_organizer = await Organizer.find_one({"_id": ObjectId(organizer_id)})
        updated_organizer["id"] = str(updated_organizer.pop("_id"))
        return OrganizerRead(**updated_organizer)
    raise HTTPException(status_code=404, detail="Organizer not found")

@router.delete("/{organizer_id}")
async def delete_organizer(organizer_id: str):
    if not ObjectId.is_valid(organizer_id):
        raise HTTPException(status_code=400, detail="Invalid organizer ID")

    result = await Organizer.delete_one({"_id": ObjectId(organizer_id)})
    if result.deleted_count == 1:
        return {"message": "Organizer deleted successfully"}
    raise HTTPException(status_code=404, detail="Organizer not found")


@router.get("/search", response_model=List[OrganizerRead])
async def search_organizers(
    fullname: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
):
    query = {}
 
    if fullname:
        query["fullname"] = {"$regex": fullname, "$options": "i"}  
    if status:
        query["status"] = status
    if department:
        query["department"] = department


    organizers = await Organizer.find(query).to_list()
    if organizers:
        for organizer in organizers:
            organizer["id"] = str(organizer.pop("_id"))
            organizer.pop("password", None)  
        return [OrganizerRead(**organizer) for organizer in organizers]
    
    raise HTTPException(status_code=404, detail="No organizers match the search criteria")

@router.get("/absent", response_model=List[OrganizerRead])
async def get_absent_organizers():
    organizers = await Organizer.find({"is_absent": True}).to_list()
    if organizers:
        for organizer in organizers:
            organizer["id"] = str(organizer.pop("_id"))
            organizer.pop("password", None)  
        return [OrganizerRead(**organizer) for organizer in organizers]
    raise HTTPException(status_code=404, detail="No absent organizers found")


@router.get("/present", response_model=List[OrganizerRead])
async def get_present_organizers():
    organizers = await Organizer.find({"is_absent": False}).to_list()
    if organizers:
        for organizer in organizers:
            organizer["id"] = str(organizer.pop("_id"))
            organizer.pop("password", None)  
        return [OrganizerRead(**organizer) for organizer in organizers]
    raise HTTPException(status_code=404, detail="No present organizers found")

@router.get("/organizer/statistics")
async def get_organizer_statistics():
    total_organizers = await Organizer.count_documents({})
    present_organizers = await Organizer.count_documents({"is_absent": False})
    absent_organizers = await Organizer.count_documents({"is_absent": True})
    free_organizers = await Organizer.count_documents({"status": "free"})

    return {
        "total_organizers": total_organizers,
        "present_organizers": present_organizers,
        "absent_organizers": absent_organizers,
        "free_organizers": free_organizers
    }
