from pydantic import BaseModel, EmailStr
from typing import Optional

class AdminBase(BaseModel):
    full_name: str
    department: str
    phone: str
    email: EmailStr
    profile_image: Optional[str] = None

class AdminCreate(AdminBase):
    password: str

class AdminUpdate(AdminBase):
    full_name: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    profile_image: Optional[str] = None

class AdminRead(AdminBase):
    id: str
