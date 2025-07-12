import requests
import json

class Sidemenstats:

    def __init__(self, api_key, channel_id):
        self.api_key = api_key
        self.channel_id = channel_id
        self.channels_stats = None
        self.video_data = None

    def get_sidemen_stats(self):
        url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={self.channel_id}&key={self.api_key}"
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        try:
            data = data["items"][0]["statistics"]
        except:
            data = None
        self.channels_stats = data
        return data

    def get_uploads_playlist_id(self):
        url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={self.channel_id}&key={self.api_key}"
        response = requests.get(url)
        data = response.json()
        try:
            return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        except:
            return None

    def get_channel_videos(self):
        uploads_playlist_id = self.get_uploads_playlist_id()
        if not uploads_playlist_id:
            print("Could not fetch uploads playlist ID.")
            return {}

        videos = {}
        base_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={uploads_playlist_id}&maxResults=50&key={self.api_key}"
        print(base_url)
        next_page_token = ""

        while True:
            url = base_url
            if next_page_token:
                url += f"&pageToken={next_page_token}"

            response = requests.get(url)
            data = response.json()

            for item in data.get("items", []):
                video_id = item["contentDetails"]["videoId"]
                videos[video_id] = {}

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        return videos

    def get_video_data(self):
        self.video_data = self.get_channel_videos()
        print(f"Total videos found: {len(self.video_data)}")
        print(self.video_data)

    def dump(self):
        if self.channels_stats is None:
            return
        channel_title = "Sidemen_channel"
        channel_title = channel_title.replace(" ", "_").lower()
        file_name = channel_title + ".json"
        with open(file_name, "w") as f:
            json.dump(self.channels_stats, f, indent=4)

        print("File dumped successfully")
