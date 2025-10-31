import os
import streamlit as st
import pandas as pd
import plotly.express as px
from ensembledata.api import EDClient
from tiktok_analysis.src.dashboard.gpt_report import generate_report

API_TOKEN = "f5Kbwj1Kz03O2GXV"  # Your API token

st.set_page_config(page_title="Unified TikTok Analytics Dashboard", layout="wide")
st.title("TikTok Hashtag & Trend Analytics Dashboard 📊")

# --- SECTION 1: Hashtag Analysis ---
st.header("1. TikTok Hashtag Analysis")
with st.sidebar:
    st.subheader("Hashtag Analysis Settings")
    hashtag = st.text_input("Enter hashtag to analyze (without #)", value="")
    max_pages = st.slider("Number of pages to analyze", 1, 10, 3, help="Each page contains up to 20 posts. More pages means more historical data but slower loading.")

def fetch_hashtag_data(token, hashtag, max_pages):
    client = EDClient(token)
    cursor = 0
    all_posts = []
    with st.spinner(f'Fetching data for #{hashtag}...'):
        for _ in range(max_pages):
            try:
                result = client.tiktok.hashtag_search(hashtag=hashtag, cursor=cursor)
                posts = result.data.get("data", [])
                processed_posts = []
                for post in posts:
                    stats = post.get('statistics', {})
                    processed_post = {
                        'desc': post.get('desc', ''),
                        'author': post.get('author', {}).get('nickname', 'Unknown'),
                        'likes': stats.get('digg_count', 0),
                        'comments': stats.get('comment_count', 0),
                        'shares': stats.get('share_count', 0),
                        'plays': stats.get('play_count', 0),
                        'duration': post.get('video', {}).get('duration', 0),
                    }
                    processed_posts.append(processed_post)
                all_posts.extend(processed_posts)
                next_cursor = result.data.get("nextCursor")
                if next_cursor is None:
                    break
                cursor = next_cursor
            except Exception as e:
                st.error(f"Error fetching data: {str(e)}")
                break
    return all_posts

if hashtag.strip() == "":
    st.info("Please enter a hashtag to analyze.")
else:
    posts = fetch_hashtag_data(API_TOKEN, hashtag, max_pages)
    if posts:
        df = pd.DataFrame(posts)
        st.subheader("Hashtag Overview")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Posts", len(df))
        with col2:
            st.metric("Total Likes", df['likes'].sum())
        with col3:
            st.metric("Total Comments", df['comments'].sum())
        with col4:
            st.metric("Total Views", df['plays'].sum())
        st.subheader("Engagement Analysis")
        fig_scatter = px.scatter(df, x='likes', y='comments', size='plays', hover_data=['desc'], title='Likes vs Comments (size=plays)')
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.subheader("Top Posts")
        top_posts = df.nlargest(10, 'likes')[['desc', 'likes', 'comments', 'shares', 'plays']]
        st.dataframe(top_posts)
        st.download_button(
            label="Download data as CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name=f'tiktok_{hashtag}_data.csv',
            mime='text/csv',
        )

# --- SECTION 2: TikTok Trend Analysis ---
st.header("2. TikTok Trend Analysis (Dataset)")
dataset_path = os.path.join("tiktok_analysis", "data", "tiktok_dataset.csv")
if not os.path.exists(dataset_path):
    st.warning(f"Dataset not found at {dataset_path}. Please check the file location.")
else:
    df2 = pd.read_csv(dataset_path)
    # Add engagement column if not present
    if 'engagement' not in df2.columns:
        df2['engagement'] = (
            df2['video_view_count'] +
            df2['video_like_count'] +
            df2['video_share_count'] +
            df2['video_comment_count'] +
            df2['video_download_count']
        )
    status = st.selectbox("Select Author Ban Status", df2['author_ban_status'].unique())
    filtered = df2[df2['author_ban_status'] == status]
    top_videos = filtered.nlargest(20, 'engagement')
    st.subheader("Top 20 Videos by Engagement")
    fig1 = px.bar(
        top_videos,
        x='engagement',
        y='video_id',
        title=f'Top 20 Videos by Engagement ({status})',
        orientation='h'
    )
    fig1.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig1, use_container_width=True)
    engagement_types = top_videos[['video_id', 'video_view_count', 'video_like_count', 'video_share_count', 'video_comment_count', 'video_download_count']]
    engagement_melted = engagement_types.melt(
        id_vars='video_id',
        var_name='Type',
        value_name='Count'
    )
    fig2 = px.bar(
        engagement_melted,
        x='video_id',
        y='Count',
        color='Type',
        title=f'Engagement Breakdown (Stacked) ({status})',
        barmode='stack'
    )
    fig2.update_layout(xaxis_title="Video ID", yaxis_title="Engagement Count")
    st.plotly_chart(fig2, use_container_width=True)
    # --- SECTION 3: ChatGPT AI Report ---
    st.header("3. ChatGPT AI Report (Experimental)")
    st.write("Generate an AI-powered summary of the filtered TikTok trend data.")
    if st.button("Generate AI Report"):
        with st.spinner("Generating report..."):
            summary = filtered[['video_view_count', 'video_like_count', 'video_share_count', 'video_comment_count', 'video_download_count']].describe().head(10).to_string()
            report = generate_report(summary)
        st.markdown(report)
