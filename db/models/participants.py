from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Participant(BaseModel):
    id: int = Field(..., description="Unique identifier")
    full_name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    team: Optional[str] = Field(None, description="Team name")
    password: str = Field(..., description="Hashed password")


