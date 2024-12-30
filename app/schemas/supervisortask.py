from pydantic import BaseModel
from typing import Optional

class SupervisorTaskBase(BaseModel):
    task_id: int
    supervisor_id: int

class SupervisorTaskCreate(SupervisorTaskBase):
    pass

class SupervisorTaskRead(SupervisorTaskBase):
    pass

class SupervisorTaskUpdate(BaseModel):
    task_id: Optional[int] = None
    supervisor_id: Optional[int] = None
