from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class SupervisorTask(BaseModel):
    task_id: str = Field(..., description="Task identifier")
    supervisor_id: str = Field(..., description="Supervisor identifier")
