import streamlit as st
import pandas as pd
import plotly.express as px
from ensembledata.api import EDClient

# Set your API token here
API_TOKEN = "d27oMjsSy7Lw4G8K"  # Your API token

# Page config
st.set_page_config(page_title="TikTok Hashtag Analytics Dashboard", layout="wide")

# Title
st.title("TikTok Hashtag Analytics Dashboard 📊")

# Sidebar for inputs
with st.sidebar:
    st.header("Analysis Settings")
    
    # Hashtag input
    hashtag = st.text_input("Enter hashtag to analyze (without #)", value="trending")
    
    # Number of pages
    max_pages = st.slider("Number of pages to analyze", 1, 10, 5, 
                         help="More pages = more data but slower analysis")

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
try:
    # Fetch data using the predefined API token
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
                               hover_data=['desc', 'author'],
                               title='Likes vs Comments (size represents play count)')
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Bar chart of top posts by likes
        fig_bar = px.bar(df.nlargest(10, 'likes'),
                        x='desc',
                        y=['likes', 'comments', 'shares'],
                        title='Top 10 Posts by Engagement',
                        barmode='group')
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Top posts table
        st.header("Top Posts")
        top_posts = df.nlargest(10, 'likes')[['desc', 'author', 'likes', 'comments', 'shares', 'plays']]
        st.dataframe(top_posts)
        
        # Additional Analysis
        st.header("Additional Insights")
        
        # Average engagement metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg Likes per Post", f"{df['likes'].mean():.1f}")
        with col2:
            st.metric("Avg Comments per Post", f"{df['comments'].mean():.1f}")
        with col3:
            st.metric("Avg Views per Post", f"{df['plays'].mean():.1f}")
        
        # Download option
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=csv.encode('utf-8'),
            file_name=f'tiktok_{hashtag}_data.csv',
            mime='text/csv',
        )
    else:
        st.warning(f"No posts found for #{hashtag}. Try a different hashtag!")

except Exception as e:
    st.error(f"Error occurred: {str(e)}")
    st.info("If you're seeing an authentication error, please check the API token in the source code.")