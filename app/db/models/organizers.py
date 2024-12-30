from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Organizer(BaseModel):
    id: str = Field(..., description="Unique identifier")
    full_name: str = Field(..., description="Full name")
    phone: str = Field(..., description="Phone number")
    status: str = Field(..., description="Available, Busy, or Time Off")
    department: str = Field(..., description="Associated department")
    password: str = Field(..., description="Hashed password")
    is_absent: bool = Field(False, description="Indicates if the organizer is absent")
