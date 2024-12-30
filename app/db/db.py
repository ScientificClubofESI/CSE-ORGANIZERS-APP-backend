import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import logging

load_dotenv()
MONGO_URI = os.getenv("DATA_BASE")

client = AsyncIOMotorClient(MONGO_URI)

database = client["Organizers-App"]

your_collection = database["TEST"]
Admin = database["admins"]
Organizer = database["organizers"]
Participant= database["participants"]
Task = database["tasks"]
Event = database["events"]
AssignedTask= database["assigned_tasks"]
ScannedTask= database["scanned_tasks"]
SupervisorTask= database["supervisor_tasks"]


