import os
from fastapi import FastAPI
from api.endpoints.admin import router as admin_router
from api.endpoints.assignedtask import router as assigned_task_router
from api.endpoints.event import router as event_router
from api.endpoints.organizers import router as organizer_router
from api.endpoints.participants import router as participant_router
from api.endpoints.scannedtask import router as scanned_task_router
from api.endpoints.supervisortask import router as supervisor_task_router
from api.endpoints.tasks import router as task_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

FRONT_URL = os.getenv("FRONTEND_URL")

# Allow frontend to access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONT_URL,"http://localhost:3000"],  # Adjust for your frontend domain
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

port = int(os.environ.get("PORT", 8000))  # Use 8000 as a fallback


@app.get("/")
async def root():
    return {"message": "Welcome to the Organizer App API!"}

# Include all routers
app.include_router(admin_router, prefix="/admins", tags=["Admins"])
app.include_router(assigned_task_router, prefix="/assigned-tasks", tags=["Assigned Tasks"])
app.include_router(event_router, prefix="/events", tags=["Events"])
app.include_router(organizer_router, prefix="/organizers", tags=["Organizers"])
app.include_router(participant_router, prefix="/participants", tags=["Participants"])
app.include_router(scanned_task_router, prefix="/scanned-tasks", tags=["Scanned Tasks"])
app.include_router(supervisor_task_router, prefix="/supervisor-tasks", tags=["Supervisor Tasks"])
app.include_router(task_router, prefix="/tasks", tags=["Tasks"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)
