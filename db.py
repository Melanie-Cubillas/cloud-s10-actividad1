from pymongo import MongoClient
import os

MONGODB_URI = os.getenv("MONGO_URL")

client = MongoClient(MONGODB_URI)

db = client["inventario_db"]

collection = db["productos"]
