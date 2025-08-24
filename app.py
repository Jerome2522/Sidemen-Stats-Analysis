import streamlit as st
import pandas as pd
import pymongo
import altair as alt
import isodate
import os

st.set_page_config(page_title="Sidemen YouTube Dashboard", layout="wide")

image_path = "sidemenbanner.jpeg"
st.image(image_path, use_container_width=True)

st.title("📊 Sidemen YouTube Stats")
st.caption(
    "Interactive dashboard powered by Streamlit, Data pulled from YouTube API "
    "and backed up in MongoDB, Occasional data updates using Apache Airflow."
)

# ---- DB Connection ----
@st.cache_resource
def init_connection():
    mongo_uri = st.secrets["mongo"]["uri"]  # from secrets.toml
    client = pymongo.MongoClient(mongo_uri)
    return client

client = init_connection()
db = client["Sidemen"]
collection = db["sidemen_stats"]

# ---- Load Data ----
@st.cache_data
def load_data():
    data = list(collection.find())
    df = pd.DataFrame(data)

    if df.empty:
        return df

    df["published_at"] = pd.to_datetime(df["published_at"])
    df["pull_date"] = pd.to_datetime(df["pull_date"])

    df["duration"] = df["duration"].apply(
        lambda x: isodate.parse_duration(x).total_seconds() / 60
    )

    if "_id" in df.columns:
        df["_id"] = df["_id"].astype(str)

    return df

df = load_data()

# ---- Overview ----
if not df.empty:
    st.subheader("📌 Channel Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Subscribers", f"{df['channel_subscriberCount'].iloc[-1]:,}")
    col2.metric("Total Views", f"{df['channel_viewCount'].iloc[-1]:,}")
    col3.metric("Video Count", f"{df['channel_videoCount'].iloc[-1]:,}")
    col4.metric("Latest Data Pull", df["pull_date"].max().strftime("%Y-%m-%d"))

    # Tabs
    tabs = st.tabs(
        [
            "📈 Trends Over Time",
            "⏱ Video Duration",
            "🏆 Top Videos",
            "⚖️ Correlations",
            "📊 Averages",
        ]
    )

    # ---- Trends ----
    with tabs[0]:
        st.subheader("📈 Views, Likes, Comments Over Time")
        for metric in ["views", "likes", "comments"]:
            chart = (
                alt.Chart(df)
                .mark_line(point=True)
                .encode(
                    x=alt.X("published_at:T", title="Published Date"),
                    y=alt.Y(f"{metric}:Q", title=metric.capitalize()),
                    tooltip=["title", metric, "published_at"],
                )
                .properties(
                    title=f"{metric.capitalize()} Over Time",
                    width=900,
                    height=400,
                )
            )
            st.altair_chart(chart, use_container_width=True)

    # ---- Duration ----
    with tabs[1]:
        st.subheader("⏱ Video Duration Distribution")
        duration_chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("duration:Q", bin=alt.Bin(maxbins=30), title="Duration (minutes)"),
                y=alt.Y("count()", title="Number of Videos"),
                tooltip=["count()"],
            )
            .properties(
                title="Distribution of Video Durations",
                width=900,
                height=400,
            )
        )
        st.altair_chart(duration_chart, use_container_width=True)

    # ---- Top Videos ----
    with tabs[2]:
        st.subheader("🏆 Top 5 Most Viewed Videos")

        # Select Top 5
        top_videos = df.sort_values(by="views", ascending=False).head(5)

        # Show Bar Chart
        chart = (
            alt.Chart(top_videos)
            .mark_bar()
            .encode(
                x=alt.X("views:Q", title="Views"),
                y=alt.Y("title:N", sort="-x", title="Video Title"),
                tooltip=["views", "likes", "comments"],
            )
            .properties(
                title="Top 5 Most Viewed Videos",
                width=900,
                height=400,
            )
        )
        st.altair_chart(chart, use_container_width=True)

        # Show Thumbnails + Stats
        st.write("### 🎬 Video Thumbnails")
        for _, row in top_videos.iterrows():
            col1, col2 = st.columns([1, 3])
            with col1:
                video_id = row["video_id"]  # make sure this column exists in df
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                st.image(thumbnail_url, width=200)
            with col2:
                st.markdown(f"**{row['title']}**")
                st.write(f"👀 {row['views']:,} views")
                st.write(f"👍 {row['likes']:,} likes")
                st.write(f"💬 {row['comments']:,} comments")
                st.write(f"📅 Published: {row['published_at'].strftime('%Y-%m-%d')}")

    # ---- Correlations ----
    with tabs[3]:
        st.subheader("⚖️ Duration vs Views")
        scatter1 = (
            alt.Chart(df)
            .mark_circle(size=60, opacity=0.6)
            .encode(
                x=alt.X("duration:Q", title="Duration (minutes)"),
                y=alt.Y("views:Q", title="Views"),
                tooltip=["title", "duration", "views"],
            )
            .properties(title="Video Duration vs Views", width=900, height=500)
        )
        st.altair_chart(scatter1, use_container_width=True)

        st.subheader("⚖️ Likes vs Comments")
        scatter2 = (
            alt.Chart(df)
            .mark_circle(size=60, opacity=0.6)
            .encode(
                x=alt.X("likes:Q", title="Likes"),
                y=alt.Y("comments:Q", title="Comments"),
                tooltip=["title", "likes", "comments"],
            )
            .properties(title="Likes vs Comments", width=900, height=500)
        )
        st.altair_chart(scatter2, use_container_width=True)

    # ---- Averages ----
    with tabs[4]:
        st.subheader("📊 Average Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Avg Views", f"{int(df['views'].mean()):,}")
        col2.metric("Avg Likes", f"{int(df['likes'].mean()):,}")
        col3.metric("Avg Comments", f"{int(df['comments'].mean()):,}")

else:
    st.warning("No data available in MongoDB.")
