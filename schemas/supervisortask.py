from pydantic import BaseModel

class SupervisorTaskBase(BaseModel):
    task_id: int
    supervisor_id: int

class SupervisorTaskCreate(SupervisorTaskBase):
    pass

class SupervisorTaskRead(SupervisorTaskBase):
    pass
