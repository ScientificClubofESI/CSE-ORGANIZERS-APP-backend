from pydantic import BaseModel
from typing import List, Optional

class ScannedTaskBase(BaseModel):
    task_id: str
    participant_qr: List[str]  # Tableau de participant_qr
class ScannedTaskCreate(ScannedTaskBase):
    pass

class ScannedTaskRead(ScannedTaskBase):
    pass

class ScannedTaskUpdate(BaseModel):
    task_id: str
    participant_qr: str
    scanned: bool