import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import time
import os

st.set_page_config(page_title="Nexus Observability Engine", page_icon="👁️", layout="wide")

DB_PATH = "database/nexus_telemetry.db"

def fetch_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 500"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

st.title("👁️ Project Nexus - Observability Engine (Layer 16)")
st.caption("Live Telemetry & Resource Tracking for Multi-Agent Workflows")

df = fetch_data()

if df.empty:
    st.warning(f"Belum ada data telemetry di {DB_PATH}. Jalankan `python main.py` untuk mulai mengirim data.")
else:
    # Reverse to chronological order for plotting
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df_plot = df.sort_values(by='timestamp')

    # Metrics row
    latest = df.iloc[0]
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Current Agent", latest['agent_name'], latest['model_name'])
    col2.metric("Response Time", f"{latest['response_time_ms']:.1f} ms")
    col3.metric("API Latency", f"{latest['api_latency']:.1f} ms")
    col4.metric("CPU Usage", f"{latest['cpu_usage']:.1f}%")
    col5.metric("RAM Usage", f"{latest['ram_usage']:.1f}%")

    st.markdown("---")
    
    # Row 1 Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("⏱️ Response Time & Latency")
        fig1 = px.line(df_plot, x='timestamp', y=['response_time_ms', 'api_latency'], 
                       color_discrete_sequence=['#FF4B4B', '#0068C9'], markers=True)
        st.plotly_chart(fig1, use_container_width=True, key="chart_latency")

    with col_chart2:
        st.subheader("💻 Resource Usage (CPU vs RAM vs GPU)")
        fig2 = px.line(df_plot, x='timestamp', y=['cpu_usage', 'ram_usage', 'gpu_usage'], 
                       color_discrete_sequence=['#00C250', '#FFB703', '#8338EC'], markers=True)
        st.plotly_chart(fig2, use_container_width=True, key="chart_resource")
        
    # Row 2 Charts
    st.subheader("🧠 Token Usage Distribution")
    fig3 = px.scatter(df_plot, x='timestamp', y='token_usage', color='model_name', 
                      size='token_usage', hover_data=['agent_name'])
    st.plotly_chart(fig3, use_container_width=True, key="chart_token")
    
    st.subheader("📋 Raw Telemetry Data (Last 10 Events)")
    st.dataframe(df.head(10), use_container_width=True)

# Polling delay & rerun
time.sleep(2)
st.rerun()
