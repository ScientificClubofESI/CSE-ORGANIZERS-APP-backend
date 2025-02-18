from typing import Optional
from pydantic import BaseModel




class OrganizerBase(BaseModel):
    email: str
    full_name: str
    phone: str
    status: str
    department: str
    is_absent: bool = False


class OrganizerCreate(OrganizerBase):
    password: str

class OrganizerUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    department: Optional[str] = None
    is_absent: Optional[bool] = None
    password: Optional[str] = None

class OrganizerRead(OrganizerBase):
    id: str

class OrganizerLoginRequest(BaseModel):
    email: str
    password: str

class OrganizerLoginResponse(OrganizerBase):
    id: str
    # This inherits all fields from OrganizerBase
