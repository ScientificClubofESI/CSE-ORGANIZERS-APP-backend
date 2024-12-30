from fastapi import FastAPI
from app.api.endpoints.admin import router as admin_router
from app.api.endpoints.assignedtask import router as assigned_task_router
from app.api.endpoints.event import router as event_router
from app.api.endpoints.organizers import router as organizer_router
from app.api.endpoints.participants import router as participant_router
from app.api.endpoints.scannedtask import router as scanned_task_router
from app.api.endpoints.supervisortask import router as supervisor_task_router
from app.api.endpoints.tasks import router as task_router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the Organizer App API!"}

app.include_router(admin_router, prefix="/admins", tags=["Admins"])
app.include_router(assigned_task_router, prefix="/assigned-tasks", tags=["Assigned Tasks"])
app.include_router(event_router, prefix="/events", tags=["Events"])
app.include_router(organizer_router, prefix="/organizers", tags=["Organizers"])
app.include_router(participant_router, prefix="/participants", tags=["Participants"])
app.include_router(scanned_task_router, prefix="/scanned-tasks", tags=["Scanned Tasks"])
app.include_router(supervisor_task_router, prefix="/supervisor-tasks", tags=["Supervisor Tasks"])
app.include_router(task_router, prefix="/tasks", tags=["Tasks"])



