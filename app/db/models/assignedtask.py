from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class AssignedTask(BaseModel):
    task_id: str = Field(..., description="Task identifier")
    organizer_id: str = Field(..., description="Organizer identifier")
