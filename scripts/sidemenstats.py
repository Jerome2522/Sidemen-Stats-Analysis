import requests
import json
from tqdm import tqdm

class Sidemenstats:

    def __init__(self, api_key, channel_id): #this function is used to initialize the class
        self.api_key = api_key
        self.channel_id = channel_id
        self.channels_stats = None
        self.video_data = None

    def get_sidemen_stats(self): #this function is used to get the channel stats
        url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={self.channel_id}&key={self.api_key}"
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        try:
            data = data["items"][0]["statistics"]
        except:
            data = None
        self.channels_stats = data
        return data

    def get_uploads_playlist_id(self): #this function is used to get the uploads playlist id of the channel
        url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={self.channel_id}&key={self.api_key}"
        response = requests.get(url)
        data = response.json()
        try:
            return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        except:
            return None

    def get_channel_videos(self): #this function is used to get the videos from the channel (ALL THE DATES, TIMES, VIDEOID ETC)
        uploads_playlist_id = self.get_uploads_playlist_id()
        if not uploads_playlist_id:
            print("Could not fetch uploads playlist ID.")
            return {}

        videos = {}
        base_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={uploads_playlist_id}&maxResults=50&key={self.api_key}"
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

    def get_video_data(self): #this function is used to get the video data from the channel
        channel_videos = self.get_channel_videos()
        parts=["snippet","statistics","contentDetails"]
        for video_id in tqdm(channel_videos):
            for part in parts:
                data=self._get_single_video_data(video_id,part)
                channel_videos[video_id].update(data)

        self.video_data = channel_videos
        return channel_videos


    def _get_single_video_data(self,video_id,part):#this function is used to get the data for a single video (using the video id and the part)
        url=f"https://www.googleapis.com/youtube/v3/videos?part={part}&id={video_id}&key={self.api_key}"
        response=requests.get(url)
        data=json.loads(response.text)
        try:
            data=data["items"][0][part]
        except:
            print(f"Error getting {part} for video {video_id}")
            data=None
        return data

    def dump(self): #this function is used to dump the channel stats to a json file
        if self.channels_stats is None or self.video_data is None:
            print("No data to dump")
            return

        fused_data={self.channel_id:{"Channel_stats":self.channels_stats,"Video_data":self.video_data}}
        
        channel_title = self.video_data.popitem()[1].get('channelTitle',  self.channel_id)
        channel_title = channel_title.replace(" ", "_").lower()
        file_name = channel_title + ".json"
        with open(file_name, "w") as f:
            json.dump(fused_data, f, indent=4)

        print("File dumped successfully")