import sqlite3
import requests
from datetime import datetime, timezone

url = "https://api-v3.mbta.com/vehicles"
params = {"filter[route]": "Red"}

response = requests.get(url, params=params, timeout=10)
response.raise_for_status()
vehicles = response.json()["data"]

collected_at = datetime.now(timezone.utc).isoformat()

conn = sqlite3.connect("mbta.db")
cur = conn.cursor()

for v in vehicles:
    attrs = v["attributes"]
    rel = v["relationships"]

    route_data = rel["route"]["data"]
    stop_data = rel["stop"]["data"]

    cur.execute(
        """
        INSERT INTO vehicle_snapshots
        (vehicle_id, route_id, current_status, stop_id, direction_id, updated_at, collected_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            v["id"],
            route_data["id"] if route_data else None,
            attrs["current_status"],
            stop_data["id"] if stop_data else None,
            attrs["direction_id"],
            attrs["updated_at"],
            collected_at,
        ),
    )

conn.commit()
conn.close()
print(f"Saved {len(vehicles)} rows.")