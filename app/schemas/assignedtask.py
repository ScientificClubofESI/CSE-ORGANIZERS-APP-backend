from pydantic import BaseModel
from typing import Optional
class AssignedTaskBase(BaseModel):
    task_id: str
    organizer_id: str

class AssignedTaskCreate(AssignedTaskBase):
    pass

class AssignedTaskRead(AssignedTaskBase):
    pass

class AssignedTaskUpdate(BaseModel):
    task_id: Optional[str] = None
    organizer_id: Optional[str] = None
