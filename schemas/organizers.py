from typing import Optional
from pydantic import BaseModel

class OrganizerBase(BaseModel):
    full_name: str
    phone: str
    status: str
    department: str
    is_absent: bool = False

class OrganizerCreate(OrganizerBase):
    password: str

class OrganizerUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    department: Optional[str] = None
    is_absent: Optional[bool] = None
    password: Optional[str] = None

class OrganizerRead(OrganizerBase):
    id: int
