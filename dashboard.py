import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="MBTA Red Line Monitor", layout="wide")
st.title("MBTA Red Line Live Monitor")

conn = sqlite3.connect("mbta.db")

df = pd.read_sql("SELECT * FROM vehicle_snapshots", conn)
stops = pd.read_sql("SELECT stop_id, name FROM stops", conn)
conn.close()

df["collected_at"] = pd.to_datetime(df["collected_at"], utc=True).dt.tz_convert("America/New_York")

# KPI cards
c1, c2, c3 = st.columns(3)
c1.metric("Total records", f"{len(df):,}")
c2.metric("Snapshots collected", df["collected_at"].nunique())
c3.metric("% of trains stopped at a station", f"{100 * (df['current_status'] == 'STOPPED_AT').mean():.1f}%")

left, right = st.columns(2)

# Chart 1: busiest stations
stopped = df[df["current_status"] == "STOPPED_AT"].merge(stops, on="stop_id")
top = stopped.groupby("name").size().sort_values(ascending=False).head(10)
left.subheader("Top 10 stations by trains stopped")
left.bar_chart(top)

# Chart 2: trains over time
over_time = df.groupby("collected_at").size()
right.subheader("Active trains over time")
right.line_chart(over_time)

st.caption("Data: MBTA V3 API, collected every 60 seconds.")