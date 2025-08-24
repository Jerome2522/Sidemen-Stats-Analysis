from sidemenstats import Sidemenstats
import os
import sys
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def main():
    """
    Main function to fetch Sidemen YouTube stats, find new videos,
    and save them to a JSONL file and a MongoDB database.
    """
    # --- Configuration ---
    API_KEY=os.getenv("YOUTUBE_API_KEY")
    if not API_KEY:
        print("Error: YOUTUBE_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    CHANNEL_ID = "UCDogdKl7t7NHzQ95aEwkdMw"
    JSONL_FILENAME = "sidemen_flat_data.jsonl"
    # Use environment variable for MongoDB URI, with a default for local development
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = "Sidemen"
    COLLECTION_NAME = "sidemen_stats"

    # --- Logic ---
    print("Using Mongo URI:", MONGO_URI)
    sidemen = Sidemenstats(API_KEY, CHANNEL_ID)
    sidemen.get_sidemen_stats()

    # Fetch all videos but filter to only new ones
    video_data = sidemen.get_incremental_video_data()

    if video_data:
        # Filter out videos that already exist in the database
        new_videos_only = sidemen.filter_new_videos_only(
            video_data, MONGO_URI, DB_NAME, COLLECTION_NAME
        )

        if new_videos_only:
            sidemen.dump_flat_data(
                new_videos_only,
                filename=JSONL_FILENAME,
                to_mongo=True,
                mongo_uri=MONGO_URI,
                db_name=DB_NAME,
                collection_name=COLLECTION_NAME
            )
        else:
            print("No new videos found to process.")
    else:
        print("No video data fetched.")


if __name__ == "__main__":
    main()