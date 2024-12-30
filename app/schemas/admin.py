from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class AdminBase(BaseModel):
    full_name: str
    department: str
    phone: str
    email: EmailStr
    profile_image: Optional[str] = None

class AdminCreate(AdminBase):
    password: str

class AdminUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_image: Optional[str] = None
    password: Optional[str] = None

class AdminRead(AdminBase):
    id: str
