import streamlit as st
import pandas as pd
import pymongo
import os
from dotenv import load_dotenv
import altair as alt
import isodate

load_dotenv()  # Load environment variables from .env file

st.title("Sidemen YouTube Stats")
st.write("This app displays statistics about the Sidemen YouTube channel.")

mongo_uri = os.getenv("MONGO_URI")
client = pymongo.MongoClient(mongo_uri)
db = client["Sidemen"]
collection = db["sidemen_stats"]
data=list(collection.find())
df = pd.DataFrame(data)

df['published_at']=pd.to_datetime(df['published_at'])
df['pull_date']=pd.to_datetime(df['pull_date'])

df['duration']=df['duration'].apply(lambda x : isodate.parse_duration(x).total_seconds()/60)

# Convert ObjectId to string for Streamlit compatibility
if '_id' in df.columns:
    df['_id'] = df['_id'].astype(str)

st.subheader("Views, Likes, Comments Over Time")
for metric in ['views','likes','comments']:
    chart = alt.Chart(df).mark_line().encode(
        x='published_at:T',
        y=alt.Y(f'{metric}:Q', title=metric.capitalize()),
        tooltip=['title', metric, 'published_at']
    ).properties(title=f"{metric.capitalize()} Over Time")
    st.altair_chart(chart, use_container_width=True)

st.subheader("Video Duration Distribution")
duration_chart=alt.Chart(df).mark_bar().encode(
    x=alt.X('duration:Q', bin=alt.Bin(maxbins=30), title='Duration (minutes)'),
    y='count()',
    tooltip=['count()']
).properties(title="Distribution of Video Durations")
st.altair_chart(duration_chart, use_container_width=True)