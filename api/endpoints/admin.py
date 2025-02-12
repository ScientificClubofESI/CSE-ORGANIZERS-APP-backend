from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from db.models.admin import Admin
from schemas.admin import AdminCreate, AdminRead, AdminUpdate
from passlib.context import CryptContext
from typing import List
from db import db

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/", response_model=AdminRead)
async def create_admin(admin: AdminCreate):
    hashed_password = hash_password(admin.password)
    admin_data = admin.dict()
    admin_data["password"] = hashed_password
    
    result = await db.admin_collection.insert_one(admin_data)
    admin_data["id"] = str(result.inserted_id)
    admin_data.pop("password")
    return AdminRead(**admin_data)

@router.get("/", response_model=List[AdminRead])
async def get_all_admins():
    admins_cursor = db.admin_collection.find()
    admins = await admins_cursor.to_list(None)
    if admins:
        for admin in admins:
            admin["id"] = str(admin.pop("_id"))
            admin.pop("password", None)
        return [AdminRead(**admin) for admin in admins]
    raise HTTPException(status_code=404, detail="No admins found")

@router.get("/{admin_id}", response_model=AdminRead)
async def get_admin(admin_id: str):
    if not ObjectId.is_valid(admin_id):
        raise HTTPException(status_code=400, detail="Invalid admin ID")
    
    admin = await db.admin_collection.find_one({"_id": ObjectId(admin_id)})
    if admin:
        admin["id"] = str(admin.pop("_id"))
        admin.pop("password", None)
        return AdminRead(**admin)
    raise HTTPException(status_code=404, detail="Admin not found")

@router.put("/{admin_id}", response_model=AdminRead)
async def update_admin(admin_id: str, admin: AdminUpdate):
    if not ObjectId.is_valid(admin_id):
        raise HTTPException(status_code=400, detail="Invalid admin ID")
    
    update_data = {k: v for k, v in admin.dict().items() if v is not None}
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])
    
    result = await db.admin_collection.update_one(
        {"_id": ObjectId(admin_id)}, 
        {"$set": update_data}
    )
    
    if result.modified_count == 1:
        updated_admin = await db.admin_collection.find_one({"_id": ObjectId(admin_id)})
        updated_admin["id"] = str(updated_admin.pop("_id"))
        updated_admin.pop("password", None)
        return AdminRead(**updated_admin)
    raise HTTPException(status_code=404, detail="Admin not found")

@router.delete("/{admin_id}")
async def delete_admin(admin_id: str):
    if not ObjectId.is_valid(admin_id):
        raise HTTPException(status_code=400, detail="Invalid admin ID")
    
    result = await db.admin_collection.delete_one({"_id": ObjectId(admin_id)})
    if result.deleted_count == 1:
        return {"message": "Admin deleted successfully"}
    raise HTTPException(status_code=404, detail="Admin not found")

@router.get("/search/", response_model=List[AdminRead])
async def search_admin(full_name: str = Query(None), email: str = Query(None)):
    if not full_name and not email:
        raise HTTPException(status_code=400, detail="Either fullname or email must be provided")
    
    query = {}
    if full_name:
        query["full_name"] = {"$regex": full_name, "$options": "i"}  # Case-insensitive search
    if email:
        query["email"] = {"$regex": email, "$options": "i"}
    
    admins = await db.admin_collection.find(query).to_list(None)
    if admins:
        for admin in admins:
            admin["id"] = str(admin.pop("_id"))
            admin.pop("password", None)
        return [AdminRead(**admin) for admin in admins]
    raise HTTPException(status_code=404, detail="No matching admins found")