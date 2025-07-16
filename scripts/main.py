from sidemenstats import Sidemenstats
import os

API_KEY = "AIzaSyC4IXe1lAD7nXdoK8cGEeTEewZLIEsW7iQ"
channel_id = "UCDogdKl7t7NHzQ95aEwkdMw"
jsonl_filename = "sidemen_flat_data.jsonl"
mongo_uri = "mongodb://localhost:27017/"
db_name = "Sidemen"
collection_name = "sidemen_stats"

# Overwrite the JSONL file each run for clean output
def clear_jsonl_file(filename):
    if os.path.exists(filename):
        os.remove(filename)

clear_jsonl_file(jsonl_filename)

sidemen = Sidemenstats(API_KEY, channel_id)
sidemen.get_sidemen_stats()
video_data = sidemen.get_video_data()
sidemen.dump_flat_data(
    video_data,
    filename=jsonl_filename,
    to_mongo=True,
    mongo_uri=mongo_uri,
    db_name=db_name,
    collection_name=collection_name
)