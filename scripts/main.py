from sidemenstats import Sidemenstats
import os

API_KEY = "AIzaSyC4IXe1lAD7nXdoK8cGEeTEewZLIEsW7iQ"
channel_id = "UCDogdKl7t7NHzQ95aEwkdMw"
jsonl_filename = "sidemen_flat_data.jsonl"
# Use environment variable for MongoDB URI, with Docker container name as default
mongo_uri = os.getenv('MONGO_URI', 'mongodb://192.168.1.8:27017/')
db_name = "Sidemen"
collection_name = "sidemen_stats"

# Overwrite the JSONL file each run for clean output
def clear_jsonl_file(filename):
    if os.path.exists(filename):
        os.remove(filename)

# Don't clear the file for incremental updates
# clear_jsonl_file(jsonl_filename)

sidemen = Sidemenstats(API_KEY, channel_id)
sidemen.get_sidemen_stats()

# Fetch all videos but filter to only new ones
video_data = sidemen.get_incremental_video_data()

if video_data:
    # Filter out videos that already exist in the database
    new_videos_only = sidemen.filter_new_videos_only(video_data, mongo_uri, db_name, collection_name)
    
    if new_videos_only:
        sidemen.dump_flat_data(
            new_videos_only,
            filename=jsonl_filename,
            to_mongo=True,
            mongo_uri=mongo_uri,
            db_name=db_name,
            collection_name=collection_name
        )
    else:
        print("No new videos found to process.")
else:
    print("No video data fetched.")