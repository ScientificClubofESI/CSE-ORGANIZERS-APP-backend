import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from db.db import your_collection
from api.endpoints.admin import router as admin_router
from api.endpoints.assignedtask import router as assigned_task_router
from api.endpoints.event import router as event_router
from api.endpoints.organizers import router as organizer_router
from api.endpoints.participants import router as participant_router
from api.endpoints.scannedtask import router as scanned_task_router
from api.endpoints.supervisortask import router as supervisor_task_router
from api.endpoints.tasks import router as task_router

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

# Get port from environment variable for Render deployment
port = int(os.environ.get("PORT", 10000))

# Helper function to format ObjectId as string
def to_json(data):
    if "_id" in data:
        data["_id"] = str(data["_id"])
    return data

# Request model
class Item(BaseModel):
    name: str
    description: str
    price: float

@app.get("/")
async def read_root():
    return {"message": "API is running"}

@app.get("/items")
async def read_items():
    items = await your_collection.find().to_list(100)
    return [to_json(item) for item in items]

@app.post("/items")
async def create_item(item: Item):
    result = await your_collection.insert_one(item.dict())
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Item could not be added")
    return {"id": str(result.inserted_id)}

@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    result = await your_collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"detail": "Item deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)