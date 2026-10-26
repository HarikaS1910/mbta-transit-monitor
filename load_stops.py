import sqlite3
import requests

url = "https://api-v3.mbta.com/stops"
params = {"filter[route]": "Red", "include": "child_stops"}

response = requests.get(url, params=params, timeout=10)
response.raise_for_status()

body = response.json()
stops = body["data"] + body.get("included", [])

conn = sqlite3.connect("mbta.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS stops (
    stop_id TEXT PRIMARY KEY,
    name TEXT,
    platform_name TEXT
)
""")

for s in stops:
    attrs = s["attributes"]
    cur.execute(
        "INSERT OR REPLACE INTO stops (stop_id, name, platform_name) VALUES (?, ?, ?)",
        (s["id"], attrs["name"], attrs["platform_name"]),
    )

conn.commit()
conn.close()
print(f"Loaded {len(stops)} stops.")