from pydantic import BaseModel

class ScannedTaskBase(BaseModel):
    task_id: int
    participant_qr: str
    scanned: bool = False

class ScannedTaskCreate(ScannedTaskBase):
    pass

class ScannedTaskRead(ScannedTaskBase):
    pass
