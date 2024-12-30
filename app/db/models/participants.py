from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Participant(BaseModel):
    qr_code: str = Field(..., description="Unique QR code")
    full_name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    team: Optional[str] = Field(None, description="Team name")
    password: str = Field(..., description="Hashed password")
