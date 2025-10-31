import os
import streamlit as st
import pandas as pd
import plotly.express as px
from ensembledata.api import EDClient

# Set your API token here
API_TOKEN = "f5Kbwj1Kz03O2GXV"  # Your API token

# Page config
st.set_page_config(page_title="TikTok Analytics Dashboard", layout="wide")

# Title
st.title("TikTok Hashtag Analytics Dashboard 📊")

# Sidebar for inputs
with st.sidebar:
    st.header("Analysis Settings")
    
    # Hashtag input
    hashtag = st.text_input("Enter hashtag to analyze (without #)", value="")
    
    # Number of pages
    max_pages = st.slider("Number of pages to analyze", 1, 10, 3, 
                         help="Each page contains up to 20 posts. More pages means more historical data but slower loading.")

def fetch_hashtag_data(token, hashtag, max_pages):
    client = EDClient(token)
    cursor = 0
    all_posts = []
    
    with st.spinner(f'Fetching data for #{hashtag}...'):
        for _ in range(max_pages):
            try:
                result = client.tiktok.hashtag_search(hashtag=hashtag, cursor=cursor)
                posts = result.data.get("data", [])
                
                # Extract relevant data from each post
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

# Main content
# Main content
# Fetch data using the predefined API token

# Only fetch and display data if a hashtag is entered
if hashtag.strip() == "":
    st.info("Please enter a hashtag to analyze.")
else:
    posts = fetch_hashtag_data(API_TOKEN, hashtag, max_pages)
    if posts:
        # Convert to DataFrame
        df = pd.DataFrame(posts)
        # Display basic stats
        st.header("Overview")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Posts", len(df))
        with col2:
            st.metric("Total Likes", df['likes'].sum())
        with col3:
            st.metric("Total Comments", df['comments'].sum())
        with col4:
            st.metric("Total Views", df['plays'].sum())
        # Engagement visualization
        st.header("Engagement Analysis")
        # Scatter plot of likes vs comments
        fig_scatter = px.scatter(df, 
                               x='likes', 
                               y='comments',
                               size='plays',
                               hover_data=['desc'],
                               title='Likes vs Comments (size represents play count)')
        st.plotly_chart(fig_scatter, use_container_width=True)
        # Top posts table
        st.header("Top Posts")
        top_posts = df.nlargest(10, 'likes')[['desc', 'likes', 'comments', 'shares', 'plays']]
        st.dataframe(top_posts)
        # Download option
        st.download_button(
            label="Download data as CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name=f'tiktok_{hashtag}_data.csv',
            mime='text/csv',
        )