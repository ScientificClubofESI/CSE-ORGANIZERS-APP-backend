from pydantic import BaseModel
from typing import Optional

class ScannedTaskBase(BaseModel):
    task_id: str
    participant_qr: str
    scanned: bool = False

class ScannedTaskCreate(ScannedTaskBase):
    pass

class ScannedTaskRead(ScannedTaskBase):
    pass

class ScannedTaskUpdate(BaseModel):
    task_id: Optional[str] = None
    participant_qr: Optional[str] = None
    scanned: Optional[bool] = False