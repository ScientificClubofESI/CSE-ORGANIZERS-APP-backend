from fastapi import APIRouter, HTTPException ,Query
from bson import ObjectId
from app.db.db import Admin
from app.schemas.admin import AdminCreate, AdminRead, AdminUpdate
from passlib.context import CryptContext
from typing import List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

router = APIRouter()

@router.post("/", response_model=AdminRead)
async def create_admin(admin: AdminCreate):
    hashed_password = hash_password(admin.password)
    admin_data = admin.dict()
    admin_data["password"] = hashed_password
    result = await Admin.insert_one(admin_data)
    admin_data["id"] = str(result.inserted_id)
    admin_data.pop("password")
    return AdminRead(**admin_data)

@router.get("/", response_model=List[AdminRead])
async def get_all_admins():
    admins = await Admin.find().to_list()
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

    admin = await Admin.find_one({"_id": ObjectId(admin_id)})
    if admin:
        admin["id"] = str(admin.pop("_id"))
        return AdminRead(**admin)
    raise HTTPException(status_code=404, detail="Admin not found")

@router.put("/{admin_id}", response_model=AdminRead)
async def update_admin(admin_id: str, admin: AdminUpdate):
    if not ObjectId.is_valid(admin_id):
        raise HTTPException(status_code=400, detail="Invalid admin ID")

    update_data = {k: v for k, v in admin.dict().items() if v is not None}
    result = await admin_colleAdminction.update_one({"_id": ObjectId(admin_id)}, {"$set": update_data})

    if result.modified_count == 1:
        updated_admin = await Admin.find_one({"_id": ObjectId(admin_id)})
        updated_admin["id"] = str(updated_admin.pop("_id"))
        return AdminRead(**updated_admin)

    raise HTTPException(status_code=404, detail="Admin not found")

@router.delete("/{admin_id}")
async def delete_admin(admin_id: str):
    if not ObjectId.is_valid(admin_id):
        raise HTTPException(status_code=400, detail="Invalid admin ID")

    result = await Admin.delete_one({"_id": ObjectId(admin_id)})

    if result.deleted_count == 1:
        return {"message": "Admin deleted successfully"}

    raise HTTPException(status_code=404, detail="Admin not found")

@router.get("/1/search", response_model=List[AdminRead])
async def search_admin(full_name: str = Query(None), email: str = Query(None)):
    if not full_name and not email:
         raise HTTPException(status_code=400, detail="Either fullname or email must be provided")
    print(f"Received full_name: {full_name}, email: {email}")
    query = {}
    if full_name:
         query["full_name"] = full_name
    if email:
         query["email"] = email
    print(f"Query: {query}")
    admins = await Admin.find(query).to_list()
    print(admins)
    if admins:
         for admin in admins:
            print(admin)
            admin.pop("password", None)  # Remove password for security
            admin["id"] = str(admin.pop("_id")) 
         return [AdminRead(**admin) for admin in admins]

    raise HTTPException(status_code=404, detail="No matching admins found")
