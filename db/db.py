import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("DATA_BASE")

client = AsyncIOMotorClient(MONGO_URI)

database = client["Organizers-App"]

your_collection = database["TEST"]
admin_collection = database["admins"]
organizer_collection = database["organizers"]
participant_collection = database["participants"]
task_collection = database["tasks"]
event_collection = database["events"]
assigned_task_collection = database["assigned_tasks"]
scanned_task_collection = database["scanned_tasks"]
supervisor_task_collection = database["supervisor_tasks"]