from pydantic import BaseModel
from typing import Optional

class SupervisorTaskBase(BaseModel):
    task_id: str
    supervisor_id: str

class SupervisorTaskCreate(SupervisorTaskBase):
    pass

class SupervisorTaskRead(SupervisorTaskBase):
    pass

class SupervisorTaskUpdate(BaseModel):
    task_id: Optional[str] = None
    supervisor_id: Optional[str] = None
