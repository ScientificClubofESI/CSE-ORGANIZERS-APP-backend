import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from db.db import your_collection

app = FastAPI()
# Get port from environment variable for Render deployment
port = int(os.getenv("PORT", 10000))

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
    # Read all documents from the collection
    items = await your_collection.find().to_list(100)  # Fetch up to 100 items
    return [to_json(item) for item in items]

@app.post("/items")
async def create_item(item: Item):
    # Insert a new document into the collection
    result = await your_collection.insert_one(item.dict())
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Item could not be added")
    return {"id": str(result.inserted_id)}

@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    # Delete a document by ObjectId
    result = await your_collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"detail": "Item deleted"}

if __name__ == "__main__":
    import uvicorn
    # For deployment: bind to 0.0.0.0 to allow external access
    uvicorn.run(app, host="0.0.0.0", port=port)