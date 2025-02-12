from pydantic import BaseModel, Field
from typing import Optional, List  # Import List explicitly
from datetime import datetime

class Event(BaseModel):
    num_days: int = Field(..., description="Total number of event days")
    map_url: Optional[str] = Field(None, description="URL of the associated map")
    days: List[datetime] = Field(..., description="List of event days")  # Use List[datetime]
