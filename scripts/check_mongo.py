from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Sidemen']
collection = db['sidemen_stats']

# Count documents
count = collection.count_documents({})
print(f"Total documents: {count}")

# Show recent documents
recent = collection.find().sort('pull_date', -1).limit(3)
for doc in recent:
    print(f"Video: {doc.get('title', 'No title')} - Views: {doc.get('views', 0)}")

client.close()