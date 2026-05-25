import streamlit as st
import pandas as pd
import plotly.express as px
from src.database import DatabaseManager

st.set_page_config(page_title="Analytics Dashboard", page_icon="📊", layout="wide")

st.title("📊 Performance Analytics Dashboard")

db = DatabaseManager()


@st.cache_data(ttl=60)
def load_data():
    with db.get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM scores ORDER BY timestamp ASC", conn)
    return df


df = load_data()

if df.empty:
    st.info("No quiz data available yet. Complete a quiz to see your analytics!")
else:
    # Key Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Quizzes Taken", len(df))
    col2.metric("Average Score", f"{df['percentage'].mean():.1f}%")
    col3.metric("Highest Score", f"{df['percentage'].max():.1f}%")

    st.markdown("---")

    # Visualizations
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Performance Trend Over Time")
        fig_trend = px.line(df, x='timestamp', y='percentage', markers=True,
                            title='Accuracy Progression', template='plotly_white')
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_chart2:
        st.subheader("Scores by PNLE Set")
        fig_bar = px.box(df, x='set_name', y='percentage', color='set_name',
                         title='Set Performance Distribution')
        st.plotly_chart(fig_bar, use_container_width=True)

    # Historical Data Table
    st.subheader("Recent Attempts")
    display_df = df[['timestamp', 'set_name', 'part_name', 'score', 'total_questions', 'percentage']].copy()
    display_df['percentage'] = display_df['percentage'].apply(lambda x: f"{x:.1f}%")
    display_df = display_df.sort_values(by='timestamp', ascending=False)
    st.dataframe(display_df, use_container_width=True, hide_index=True)