from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class EventBase(BaseModel):
    num_days: int
    map_url: Optional[str] = None
    days: List[datetime]

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    num_days: Optional[int] = None
    map_url: Optional[str] = None
    days: Optional[List[datetime]] = None

class EventRead(EventBase):
    pass
