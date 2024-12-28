from pydantic import BaseModel

class AssignedTaskBase(BaseModel):
    task_id: int
    organizer_id: int

class AssignedTaskCreate(AssignedTaskBase):
    pass

class AssignedTaskRead(AssignedTaskBase):
    pass
