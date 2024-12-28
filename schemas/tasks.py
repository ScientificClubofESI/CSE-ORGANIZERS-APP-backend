from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class TaskBase(BaseModel):
    name: str
    start_time: datetime
    end_time: datetime
    day: datetime
    location: str
    description: str
    is_complete: bool = False
    is_check_in: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    day: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    is_complete: Optional[bool] = None
    is_check_in: Optional[bool] = None

class TaskRead(TaskBase):
    id: int
