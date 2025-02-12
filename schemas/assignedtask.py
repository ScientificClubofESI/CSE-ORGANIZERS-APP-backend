from pydantic import BaseModel
from typing import Optional

class AssignedTaskUpdate(BaseModel):
    task_id: Optional[str] = None
    organizer_id: Optional[str] = None

class AssignedTaskBase(BaseModel):
    task_id: int
    organizer_id: int

class AssignedTaskCreate(AssignedTaskBase):
    pass

class AssignedTaskRead(AssignedTaskBase):
    pass
