import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("DATA_BASE")

client = AsyncIOMotorClient(MONGO_URI)

database = client["Organizers-App"]

your_collection = database["TEST"]
