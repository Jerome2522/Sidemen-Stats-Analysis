import streamlit as st
import pandas as pd
import pymongo
import os
from dotenv import load_dotenv
import altair as alt
import isodate

# --------------------
# Setup
# --------------------
load_dotenv()
st.set_page_config(page_title="Sidemen YouTube Dashboard", layout="wide")

st.title("📊 Sidemen YouTube Stats")
st.caption("Interactive dashboard powered by Streamlit, Data pulled from YouTube API and backed up in MongoDB, Occasional data updates using Apache Airflow.")

# --------------------
# MongoDB Connection (cached)
# --------------------
@st.cache_resource
def init_connection():
    mongo_uri = os.getenv("MONGO_URI")
    client = pymongo.MongoClient(mongo_uri)
    return client

client = init_connection()
db = client["Sidemen"]
collection = db["sidemen_stats"]

# --------------------
# Load Data (cached)
# --------------------
@st.cache_data
def load_data():
    data = list(collection.find())
    df = pd.DataFrame(data)

    # Parse dates
    df['published_at'] = pd.to_datetime(df['published_at'])
    df['pull_date'] = pd.to_datetime(df['pull_date'])

    # Duration in minutes
    df['duration'] = df['duration'].apply(
        lambda x: isodate.parse_duration(x).total_seconds()/60
    )

    # Convert ObjectId to str
    if '_id' in df.columns:
        df['_id'] = df['_id'].astype(str)

    return df

df = load_data()

# --------------------
# Channel Overview (Metrics)
# --------------------
st.subheader("📌 Channel Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Subscribers", f"{df['channel_subscriberCount'].iloc[-1]:,}")
col2.metric("Total Views", f"{df['channel_viewCount'].iloc[-1]:,}")
col3.metric("Video Count", f"{df['channel_videoCount'].iloc[-1]:,}")
col4.metric("Latest Data Pull", df['pull_date'].max().strftime("%Y-%m-%d"))

# --------------------
# Tabs for Charts
# --------------------
tabs = st.tabs([
    "📈 Trends Over Time",
    "⏱ Video Duration",
    "🏆 Top Videos",
    "⚖️ Correlations",
    "📊 Averages"
])

# ---- Trends ----
with tabs[0]:
    st.subheader("📈 Views, Likes, Comments Over Time")
    for metric in ['views', 'likes', 'comments']:
        chart = alt.Chart(df).mark_line(point=True).encode(
            x='published_at:T',
            y=alt.Y(f'{metric}:Q', title=metric.capitalize()),
            tooltip=['title', metric, 'published_at']
        ).properties(title=f"{metric.capitalize()} Over Time")
        st.altair_chart(chart, use_container_width=True)

# ---- Duration ----
with tabs[1]:
    st.subheader("⏱ Video Duration Distribution")
    duration_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('duration:Q', bin=alt.Bin(maxbins=30), title='Duration (minutes)'),
        y='count()',
        tooltip=['count()']
    ).properties(title="Distribution of Video Durations")
    st.altair_chart(duration_chart, use_container_width=True)

# ---- Top Videos ----
with tabs[2]:
    st.subheader("🏆 Top 10 Most Viewed Videos")
    top_videos = df.sort_values(by='views', ascending=False).head(10)
    chart = alt.Chart(top_videos).mark_bar().encode(
        x='views:Q',
        y=alt.Y('title:N', sort='-x'),
        tooltip=['views', 'likes', 'comments']
    ).properties(title="Top 10 Most Viewed Videos")
    st.altair_chart(chart, use_container_width=True)

# ---- Correlations ----
with tabs[3]:
    st.subheader("⚖️ Duration vs Views")
    scatter1 = alt.Chart(df).mark_circle(size=60).encode(
        x='duration:Q',
        y='views:Q',
        tooltip=['title', 'duration', 'views']
    ).properties(title="Video Duration vs Views")
    st.altair_chart(scatter1, use_container_width=True)

    st.subheader("⚖️ Likes vs Comments")
    scatter2 = alt.Chart(df).mark_circle(size=60).encode(
        x='likes:Q',
        y='comments:Q',
        tooltip=['title', 'likes', 'comments']
    ).properties(title="Likes vs Comments")
    st.altair_chart(scatter2, use_container_width=True)

# ---- Averages ----
with tabs[4]:
    st.subheader("📊 Average Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Views", f"{int(df['views'].mean()):,}")
    col2.metric("Avg Likes", f"{int(df['likes'].mean()):,}")
    col3.metric("Avg Comments", f"{int(df['comments'].mean()):,}")
