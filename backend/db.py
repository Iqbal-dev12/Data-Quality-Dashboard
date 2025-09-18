import os
from pymongo import MongoClient

# Get MongoDB connection string from environment variables
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("❌ MONGO_URI environment variable is not set!")

# Connect to MongoDB
client = MongoClient(MONGO_URI)

# Replace with your database name
db = client["data_quality_dashboard"]


