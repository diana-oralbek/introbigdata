import streamlit as st
import pandas as pd
import plotly.express as px
from gpt_report import generate_report

st.set_page_config(page_title="TikTok Trend Dashboard", layout="wide")
st.title("📈 TikTok Trend Analysis Dashboard")

# -------------------------
# Загружаем очищенный датасет
# -------------------------
df = pd.read_csv("data/tiktok_dataset.csv")

# -------------------------
# Рассчитываем вовлечённость
# -------------------------
df['engagement'] = (
    df['video_view_count'] +
    df['video_like_count'] +
    df['video_share_count'] +
    df['video_comment_count'] +
    df['video_download_count']
)

# -------------------------
# Фильтр по author_ban_status
# -------------------------
status = st.selectbox("Select Author Ban Status", df['author_ban_status'].unique())
filtered = df[df['author_ban_status'] == status]

# -------------------------
# Топ 20 видео по вовлечённости
# -------------------------
top_videos = filtered.nlargest(20, 'engagement')

# -------------------------
# График 1: Топ-20 видео по вовлечённости
# -------------------------
fig1 = px.bar(
    top_videos,
    x='engagement',
    y='video_id',
    title=f'Top 20 Videos by Engagement ({status})',
    orientation='h'
)
fig1.update_layout(yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig1, use_container_width=True)

# -------------------------
# График 2: Структура вовлечённости по видам
# -------------------------
engagement_types = top_videos[['video_id', 'video_view_count', 'video_like_count',
                               'video_share_count', 'video_comment_count', 'video_download_count']]

# Преобразуем данные в “длинный формат”
engagement_melted = engagement_types.melt(
    id_vars='video_id',
    var_name='Type',
    value_name='Count'
)

# Стековый график
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

# -------------------------
# Генерация AI-отчёта
# -------------------------
if st.button("Generate AI Report"):
    summary = filtered[['video_view_count', 'video_like_count', 'video_share_count',
                        'video_comment_count', 'video_download_count']].describe().head(10).to_string()
    report = generate_report(summary)
    st.markdown(report)
