from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class SupervisorTask(BaseModel):
    task_id: int = Field(..., description="Task identifier")
    supervisor_id: int = Field(..., description="Supervisor identifier")
