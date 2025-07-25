import requests
import json
from tqdm import tqdm
from datetime import datetime
import logging
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)

class Sidemenstats:
    """
    Class to fetch and process YouTube channel and video statistics for Sidemen.
    """
    def __init__(self, api_key, channel_id):
        """
        Initialize with YouTube API key and channel ID.
        """
        self.api_key = api_key
        self.channel_id = channel_id
        self.channels_stats = None
        self.video_data = None

    def get_sidemen_stats(self):
        """
        Fetch channel statistics from YouTube API.
        """
        url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={self.channel_id}&key={self.api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            stats = data["items"][0]["statistics"]
        except (requests.RequestException, KeyError, IndexError, json.JSONDecodeError) as e:
            logging.error(f"Error fetching channel stats: {e}")
            stats = None
        self.channels_stats = stats
        return stats

    def get_uploads_playlist_id(self):
        """
        Fetch the uploads playlist ID for the channel.
        """
        url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={self.channel_id}&key={self.api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            playlist_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        except (requests.RequestException, KeyError, IndexError, json.JSONDecodeError) as e:
            logging.error(f"Error fetching uploads playlist ID: {e}")
            playlist_id = None
        return playlist_id

    def get_channel_videos(self):
        """
        Fetch all video IDs from the channel's uploads playlist.
        """
        uploads_playlist_id = self.get_uploads_playlist_id()
        if not uploads_playlist_id:
            logging.error("Could not fetch uploads playlist ID.")
            return {}

        videos = {}
        base_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={uploads_playlist_id}&maxResults=50&key={self.api_key}"
        next_page_token = ""

        while True:
            url = base_url
            if next_page_token:
                url += f"&pageToken={next_page_token}"
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                for item in data.get("items", []):
                    video_id = item["contentDetails"]["videoId"]
                    videos[video_id] = {}
                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break
            except (requests.RequestException, KeyError, IndexError, json.JSONDecodeError) as e:
                logging.error(f"Error fetching channel videos: {e}")
                break
        return videos

    def get_video_data(self):
        """
        Fetch detailed data for all videos in the channel.
        This version fetches all parts in a single API call per video (more efficient).
        """
        channel_videos = self.get_channel_videos()
        if not channel_videos:
            return {}
        video_ids = list(channel_videos.keys())
        batch_size = 50  # YouTube API max per call
        parts = ["snippet", "statistics", "contentDetails"]
        for i in tqdm(range(0, len(video_ids), batch_size), desc="Fetching video data"):
            batch_ids = video_ids[i:i+batch_size]
            ids_str = ",".join(batch_ids)
            url = f"https://www.googleapis.com/youtube/v3/videos?part={','.join(parts)}&id={ids_str}&key={self.api_key}"
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                for item in data.get("items", []):
                    vid = item.get("id")
                    if vid in channel_videos:
                        channel_videos[vid].update({
                            "snippet": item.get("snippet", {}),
                            "statistics": item.get("statistics", {}),
                            "contentDetails": item.get("contentDetails", {})
                        })
            except (requests.RequestException, KeyError, IndexError, json.JSONDecodeError) as e:
                logging.error(f"Error fetching video data batch: {e}")
                continue
        self.video_data = channel_videos
        return channel_videos

    def transform_video_data(self, video_id, video_data, pull_date=None):
        """
        Transform a single video's data into a flat dictionary, including channel stats.
        """
        if pull_date is None:
            pull_date = datetime.today().strftime('%Y-%m-%d')
        def safe_int(val):
            try:
                return int(val)
            except (TypeError, ValueError):
                return 0
        # Ensure channel stats are available
        if not self.channels_stats:
            self.get_sidemen_stats()
        channel_stats = self.channels_stats or {}
        try:
            snippet = video_data.get("snippet", {})
            stats = video_data.get("statistics", {})
            content = video_data.get("contentDetails", {})
            return {
                "video_id": video_id,
                "title": snippet.get("title", "Unknown Title"),
                "published_at": snippet.get("publishedAt", ""),
                "views": safe_int(stats.get("viewCount")),
                "likes": safe_int(stats.get("likeCount")),
                "comments": safe_int(stats.get("commentCount")),
                "duration": content.get("duration", ""),
                "pull_date": pull_date,
                "channel_viewCount": safe_int(channel_stats.get("viewCount")),
                "channel_subscriberCount": safe_int(channel_stats.get("subscriberCount")),
                "channel_videoCount": safe_int(channel_stats.get("videoCount"))
            }
        except Exception as e:
            logging.error(f"Error transforming data for {video_id}: {e}")
            return None

    def insert_to_mongodb(self, data_list, mongo_uri="mongodb://localhost:27017/", db_name="Sidemen", collection_name="sidemen_stats"):
        """
        Insert data into MongoDB. Accepts a list of dicts or a single dict.
        """
        from pymongo import MongoClient
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        inserted_count = 0
        try:
            if isinstance(data_list, dict):
                collection.insert_one(data_list)
                inserted_count = 1
            elif isinstance(data_list, list):
                if data_list:
                    collection.insert_many(data_list)
                    inserted_count = len(data_list)
            logging.info(f"✅ Inserted {inserted_count} records into {db_name}.{collection_name}")
        except Exception as e:
            logging.error(f"Error inserting to MongoDB: {e}")
        finally:
            client.close()

    def dump_flat_data(self, video_data_dict, filename="sidemen_flat_data.jsonl", to_mongo=False, mongo_uri="mongodb://localhost:27017/", db_name="Sidemen", collection_name="sidemen_stats"):
        """
        Saves all transformed video data into a newline-delimited JSON file.
        Optionally inserts the same data into MongoDB if to_mongo=True.
        """
        pull_date = datetime.today().strftime('%Y-%m-%d')
        count = 0
        all_flat = []
        with open(filename, "a", encoding="utf-8") as f:
            for video_id, raw_data in video_data_dict.items():
                flat = self.transform_video_data(video_id, raw_data, pull_date)
                if flat:
                    json.dump(flat, f, ensure_ascii=False)
                    f.write("\n")
                    all_flat.append(flat)
                    count += 1
        logging.info(f"✅ {count} videos written to {filename}")
        if to_mongo and all_flat:
            self.insert_to_mongodb(all_flat, mongo_uri=mongo_uri, db_name=db_name, collection_name=collection_name)
