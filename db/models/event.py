from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class Event(BaseModel):
    num_days: int = Field(..., description="Total number of event days")
    map_url: Optional[str] = Field(None, description="URL of the associated map")
    days: list[datetime] = Field(..., description="List of event days")
