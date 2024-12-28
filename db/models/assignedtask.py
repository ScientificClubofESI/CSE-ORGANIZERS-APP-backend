from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class AssignedTask(BaseModel):
    task_id: int = Field(..., description="Task identifier")
    organizer_id: int = Field(..., description="Organizer identifier")
