from sidemenstats import Sidemenstats


API_KEY="AIzaSyC4IXe1lAD7nXdoK8cGEeTEewZLIEsW7iQ"
channel_id="UCDogdKl7t7NHzQ95aEwkdMw"

sidemen=Sidemenstats(API_KEY, channel_id)
sidemen.get_sidemen_stats()
sidemen.get_video_data()
sidemen.dump()