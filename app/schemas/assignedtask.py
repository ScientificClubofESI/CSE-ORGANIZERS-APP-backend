from pydantic import BaseModel
from typing import Optional
class AssignedTaskBase(BaseModel):
    task_id: int
    organizer_id: int

class AssignedTaskCreate(AssignedTaskBase):
    pass

class AssignedTaskRead(AssignedTaskBase):
    pass

class AssignedTaskUpdate(BaseModel):
    task_id: Optional[int] = None
    organizer_id: Optional[int] = None
