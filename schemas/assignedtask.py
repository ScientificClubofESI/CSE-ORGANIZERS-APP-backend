from pydantic import BaseModel
from typing import Optional ,List

class AssignedTaskUpdate(BaseModel):
    task_id: Optional[str] = None
    organizer_id: Optional[List[str]] = None
    supervisor_id: Optional[List[str]] = None

class AssignedTaskBase(BaseModel):
    task_id: str
    organizer_id: List[str]
    supervisor_id: Optional[List[str]] = None
    
class AssignedTaskUpdate(BaseModel):
    task_id: str
    organizer_id: Optional[List[str]]=None
    supervisor_id: Optional[List[str]] = None

class AssignedTaskCreate(AssignedTaskBase):
    pass

class AssignedTaskRead(AssignedTaskBase):
    pass
