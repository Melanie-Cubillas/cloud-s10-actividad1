import os
from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "inventario_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "productos")

client = MongoClient(MONGODB_URI)

db = client[DATABASE_NAME]

collection = db[COLLECTION_NAME]
