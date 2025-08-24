import requests
import json
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
import os

api_key = os.getenv("API")
query = "Sidemen"

url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={query}&key={api_key}"

response = requests.get(url)
data = response.json()

# Pretty print result
print(json.dumps(data, indent=2))

# Extract the top channel ID
channel_id = data['items'][0]['snippet']['channelId']
print("Channel ID:", channel_id)
