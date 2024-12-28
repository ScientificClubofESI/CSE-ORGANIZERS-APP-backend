from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class ScannedTask(BaseModel):
    task_id: int = Field(..., description="Task identifier")
    participant_qr: str = Field(..., description="participant identifier")
    scanned: bool = Field(False, description="Indique si le participant a été scanné")
