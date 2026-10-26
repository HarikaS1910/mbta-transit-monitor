import sqlite3

conn = sqlite3.connect("mbta.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS vehicle_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT,
    route_id TEXT,
    current_status TEXT,
    stop_id TEXT,
    direction_id INTEGER,
    updated_at TEXT,
    collected_at TEXT
)
""")

conn.commit()
conn.close()
print("Database and table created.")