from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
MONGO_URI=os.getenv("MONGO_URI")
print("Using Mongo URI:", MONGO_URI)  # Debug print
client = MongoClient(MONGO_URI)
print(client.list_database_names())