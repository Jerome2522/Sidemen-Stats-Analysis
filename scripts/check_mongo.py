from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()  # Load environment variables from .env file

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")
print("Using Mongo URI:", mongo_uri)  # Debug print
client = MongoClient(mongo_uri)
db = client['Sidemen']
collection = db['sidemen_stats']

# Count documents
count = collection.count_documents({})
print(f"Total documents: {count}")

# Show recent documents
recent = collection.find().sort('pull_date', -1).limit(3)
for doc in recent:
    print(f"Video: {doc.get('title', 'No title')} - Views: {doc.get('views', 0)}")

client = MongoClient(mongo_uri)
db = client["Sidemen"]
collection = db["sidemen_stats"]
print("Document count:", collection.count_documents({}))

client.close()