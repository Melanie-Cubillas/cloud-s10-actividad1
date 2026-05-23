import os
from pymongo import MongoClient

MONGO_URL = os.getenv("MONGO_URL")

DATABASE_NAME = os.getenv("DATABASE_NAME", "inventario_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "productos")

client = MongoClient(MONGO_URL)

db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]
