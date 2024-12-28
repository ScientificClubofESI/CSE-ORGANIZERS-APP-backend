from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class Task(BaseModel):
    id: int = Field(..., description="Unique identifier")
    name: str = Field(..., description="Task name")
    start_time: datetime = Field(..., description="Start time")
    end_time: datetime = Field(..., description="End time")
    day: datetime = Field(..., description="Task day")
    location: str = Field(..., description="Task location")
    description: str = Field(..., description="Task details")
    is_complete: bool = Field(False, description="Task completion status")
    is_check_in: bool = Field(False, description="Indicates if it is a check-in task")
