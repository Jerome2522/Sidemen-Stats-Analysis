import streamlit as st
import pandas as pd
import pymongo
import altair as alt
import isodate
from datetime import datetime

st.set_page_config(page_title="Sidemen YouTube Dashboard", layout="wide")

# ---- Banner ----
image_path = "sidemenbanner.jpeg"
st.image(image_path, use_container_width=True)

st.title("📊 Sidemen YouTube Stats")
st.caption(
    "Interactive dashboard powered by Streamlit, data pulled from YouTube API "
    "and backed up in MongoDB. Occasionally updated via Apache Airflow."
)

# ---- DB Connection ----
@st.cache_resource
def init_connection():
    mongo_uri = st.secrets["mongo"]["uri"]
    client = pymongo.MongoClient(mongo_uri)
    return client

client = init_connection()
db = client["Sidemen"]
collection = db["sidemen_stats"]

# ---- Load Data with TTL caching (refresh every 60s) ----
@st.cache_data(ttl=60)
def load_data():
    data = list(collection.find())
    df = pd.DataFrame(data)

    if df.empty:
        return df

    if "published_at" in df.columns:
        df["published_at"] = pd.to_datetime(df["published_at"])
    if "pull_date" in df.columns:
        df["pull_date"] = pd.to_datetime(df["pull_date"])
    if "duration" in df.columns:
        df["duration"] = df["duration"].apply(
            lambda x: isodate.parse_duration(x).total_seconds() / 60
        )
    if "_id" in df.columns:
        df["_id"] = df["_id"].astype(str)

    return df

df = load_data()

# ---- Last Updated ----
st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if not df.empty:
    # ---- Overview Cards ----
    st.subheader("📌 Channel Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Subscribers", f"{df['channel_subscriberCount'].max():,}" if "channel_subscriberCount" in df.columns else "N/A")
    col2.metric("Total Views", f"{df['channel_viewCount'].max():,}" if "channel_viewCount" in df.columns else "N/A")
    col3.metric("Video Count", f"{len(df):,}")
    col4.metric("Latest Data Pull", df["pull_date"].max().strftime("%Y-%m-%d") if "pull_date" in df.columns else "N/A")

    st.markdown("---")  # separator

    # ---- Tabs for detailed analysis ----
    tabs = st.tabs(["📈 Trends", "⏱ Duration", "🏆 Top Videos", "⚖️ Correlations", "📊 Averages"])

    # ---- Trends ----
    with tabs[0]:
        st.subheader("Views, Likes & Comments Over Time")

        metrics = ["views", "likes", "comments"]

        for metric in metrics:
            if metric in df.columns:
                chart = (
                    alt.Chart(df)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X("published_at:T", title="Published Date"),
                        y=alt.Y(f"{metric}:Q", title=metric.capitalize()),
                        tooltip=["title", metric, "published_at"]
                    )
                    .properties(width=900, height=300)
                )
                st.altair_chart(chart, use_container_width=True)


    # ---- Duration ----
    with tabs[1]:
        st.subheader("Video Duration Distribution")
        if "duration" in df.columns:
            chart = (
                alt.Chart(df)
                .mark_bar()
                .encode(
                    x=alt.X("duration:Q", bin=alt.Bin(maxbins=30), title="Duration (minutes)"),
                    y=alt.Y("count()", title="Number of Videos"),
                    tooltip=["count()"]
                )
                .properties(width=900, height=400)
            )
            st.altair_chart(chart, use_container_width=True)

    # ---- Top Videos ----
    with tabs[2]:
        st.subheader("Top 5 Most Viewed Videos")
        if "views" in df.columns:
            top_videos = df.sort_values(by="views", ascending=False).head(5)
            chart = (
                alt.Chart(top_videos)
                .mark_bar()
                .encode(
                    x=alt.X("views:Q", title="Views"),
                    y=alt.Y("title:N", sort="-x", title="Video Title"),
                    tooltip=["views", "likes", "comments"]
                )
                .properties(width=900, height=400)
            )
            st.altair_chart(chart, use_container_width=True)

            # Thumbnails Grid
            st.write("### 🎬 Video Thumbnails & Stats")
            for idx, row in top_videos.iterrows():
                cols = st.columns([1.2, 0.1, 2])  # slightly larger thumbnail column
                with cols[0]:
                    video_id = row.get("video_id", "")
                    if video_id:
                        st.image(
                            f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                            width=330  # not too big, balanced
                        )
                with cols[2]:
                    st.markdown(f"**{row.get('title', '')}**")
                    st.write(f"👀 {row.get('views', 0):,} views")
                    st.write(f"👍 {row.get('likes', 0):,} likes")
                    st.write(f"💬 {row.get('comments', 0):,} comments")
                    if "published_at" in row:
                        st.write(f"📅 Published: {row['published_at'].strftime('%Y-%m-%d')}")

                # Only small spacing after each video
                if idx != len(top_videos) - 1:  # avoid extra space after last video
                    st.markdown("---")

    # ---- Correlations ----
    with tabs[3]:
        st.subheader("Correlations")
        col1, col2 = st.columns(2)
        if "duration" in df.columns and "views" in df.columns:
            scatter1 = (
                alt.Chart(df)
                .mark_circle(size=60, opacity=0.6)
                .encode(
                    x=alt.X("duration:Q", title="Duration (minutes)"),
                    y=alt.Y("views:Q", title="Views"),
                    tooltip=["title", "duration", "views"]
                )
                .properties(width=400, height=400)
            )
            col1.altair_chart(scatter1)
        if "likes" in df.columns and "comments" in df.columns:
            scatter2 = (
                alt.Chart(df)
                .mark_circle(size=60, opacity=0.6)
                .encode(
                    x=alt.X("likes:Q", title="Likes"),
                    y=alt.Y("comments:Q", title="Comments"),
                    tooltip=["title", "likes", "comments"]
                )
                .properties(width=400, height=400)
            )
            col2.altair_chart(scatter2)

    # ---- Averages ----
    with tabs[4]:
        st.subheader("Average Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Avg Views", f"{int(df['views'].mean()):,}" if "views" in df.columns else "N/A")
        col2.metric("Avg Likes", f"{int(df['likes'].mean()):,}" if "likes" in df.columns else "N/A")
        col3.metric("Avg Comments", f"{int(df['comments'].mean()):,}" if "comments" in df.columns else "N/A")

else:
    st.warning("No data available in MongoDB.")
