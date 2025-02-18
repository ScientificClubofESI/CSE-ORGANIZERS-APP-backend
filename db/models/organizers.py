from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Organizer(BaseModel):
    id: int = Field(..., description="Unique identifier")
    full_name: str = Field(..., description="Full name")
    phone: str = Field(..., description="Phone number")
    status: Optional[str] = Field("free", description="Available, Busy, or Time Off")
    department: str = Field(..., description="Associated department")
    password: str = Field(..., description="Hashed password")
    is_absent: Optional[bool] = Field(False, description="Indicates if the organizer is absent")


