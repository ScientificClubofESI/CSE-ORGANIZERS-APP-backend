from typing import Optional
from pydantic import BaseModel, EmailStr

class ParticipantBase(BaseModel):
    qr_code: str
    full_name: str
    email: EmailStr
    phone: str
    team: Optional[str] = None

class ParticipantCreate(ParticipantBase):
    password: str

class ParticipantUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    team: Optional[str] = None
    password: Optional[str] = None

class ParticipantRead(ParticipantBase):
    pass
