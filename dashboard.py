import sqlite3
import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Boston Red Line Tracker", layout="wide")

# ---------- Load data ----------
conn = sqlite3.connect("mbta.db")
df = pd.read_sql("SELECT * FROM vehicle_snapshots", conn)
stops = pd.read_sql("SELECT stop_id, name FROM stops", conn)
conn.close()

df["collected_at"] = (
    pd.to_datetime(df["collected_at"], utc=True)
    .dt.tz_convert("America/New_York")
    .dt.tz_localize(None)
)

status_labels = {
    "STOPPED_AT": "Stopped at a station",
    "INCOMING_AT": "Arriving at a station",
    "IN_TRANSIT_TO": "Moving between stations",
}
df["What the train is doing"] = df["current_status"].map(status_labels)

# ---------- Title and intro ----------
st.title("Boston Red Line Subway: Live Train Tracker")
st.markdown(
    """
**What is this?** The Red Line is a Boston subway route that runs from **Alewife** (north)
to **Braintree** and **Ashmont** (south). The MBTA, Boston's transit agency, shares the live
position of every train. This project checks those positions **once a minute**, saves them,
and shows what the data says about how the line is used.
"""
)
st.caption(
    f"Data from {df['collected_at'].min():%b %d, %I:%M %p} to "
    f"{df['collected_at'].max():%b %d, %I:%M %p} (Boston time)"
)

# ---------- Headline numbers ----------
avg_trains = round(df.groupby("collected_at").size().mean())
pct_stopped = 100 * (df["current_status"] == "STOPPED_AT").mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Trains running at a time",
    avg_trains,
    help="On average, how many Red Line trains were on the track at the same moment.",
)
c2.metric(
    "Minutes of data collected",
    df["collected_at"].nunique(),
    help="We check the train positions once a minute, so this is roughly the number of minutes tracked.",
)
c3.metric(
    "Train readings saved",
    f"{len(df):,}",
    help="One reading = where one train was at one moment.",
)
c4.metric(
    "Time trains spend stopped at stations",
    f"{pct_stopped:.0f}%",
    help="Share of readings where the train was stopped at a station with doors open.",
)

st.divider()

# ---------- Chart 1: busiest stations ----------
stopped = df[df["current_status"] == "STOPPED_AT"].merge(stops, on="stop_id")
top = (
    stopped.groupby("name").size().sort_values(ascending=False).head(10).reset_index()
)
top.columns = ["Station", "Times a train was seen stopped here"]

left, right = st.columns(2)

left.subheader("Which stations do trains stop at most?")
left.caption(
    "Each bar counts how often we saw a train stopped at that station. "
    "Alewife and Braintree lead because they are the two ends of the line, "
    "where trains wait before turning around."
)
chart1 = (
    alt.Chart(top)
    .mark_bar()
    .encode(
        x=alt.X("Times a train was seen stopped here:Q", title="Times a train was seen stopped here"),
        y=alt.Y("Station:N", sort="-x", title=None),
        tooltip=["Station", "Times a train was seen stopped here"],
    )
)
left.altair_chart(chart1, use_container_width=True)

# ---------- Chart 2: what trains are doing ----------
status_counts = (
    df["What the train is doing"].value_counts().reset_index()
)
status_counts.columns = ["What the train is doing", "Share of readings"]
status_counts["Share of readings"] = 100 * status_counts["Share of readings"] / len(df)

right.subheader("What are the trains doing?")
right.caption(
    "Of all readings, how often a train was stopped at a station, "
    "about to arrive, or moving between stations."
)
chart2 = (
    alt.Chart(status_counts)
    .mark_bar()
    .encode(
        x=alt.X("Share of readings:Q", title="% of readings"),
        y=alt.Y("What the train is doing:N", sort="-x", title=None, axis=alt.Axis(labelLimit=300)),
        tooltip=["What the train is doing", alt.Tooltip("Share of readings:Q", format=".1f")],
    )
)
right.altair_chart(chart2, use_container_width=True)

st.divider()

# ---------- Chart 3: trains over time ----------
over_time = df.groupby("collected_at").size().reset_index()
over_time.columns = ["Time", "Trains running"]

st.subheader("How many trains were running over time?")
st.caption(
    "Each point is one minute. More trains means rush hour; fewer means a quieter period. "
    "The longer the tracker runs, the clearer this pattern becomes."
)
chart3 = (
    alt.Chart(over_time)
    .mark_line(point=True)
    .encode(
        x=alt.X("Time:T", title="Time of day (Boston)"),
        y=alt.Y("Trains running:Q", title="Trains running", scale=alt.Scale(zero=True)),
        tooltip=["Time", "Trains running"],
    )
)
st.altair_chart(chart3, use_container_width=True)

st.divider()

# ---------- Takeaways ----------
st.subheader("What do the results say?")
st.markdown(
    f"""
- On average, **{avg_trains} trains** ran at the same time.
- About **{pct_stopped:.0f}%** of the time, a train was stopped at a station.
- **{top.iloc[0, 0]}** is where we saw trains stopped most often, which fits with it being the end of the line.
"""
)

st.caption("Source: MBTA V3 public API. Built with Python, SQL (SQLite) and Streamlit.")