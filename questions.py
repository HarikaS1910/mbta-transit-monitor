import sqlite3

conn = sqlite3.connect("mbta.db")
cur = conn.cursor()

print("Q1: Trains stopped at each station (all platforms combined):")
cur.execute("""
    SELECT s.name, COUNT(*) AS times_stopped
    FROM vehicle_snapshots v
    JOIN stops s ON v.stop_id = s.stop_id
    WHERE v.current_status = 'STOPPED_AT'
    GROUP BY s.name
    ORDER BY times_stopped DESC
    LIMIT 10
""")
for row in cur.fetchall():
    print(row)

print()
print("Q2: Share of trains in each status:")
cur.execute("""
    SELECT current_status,
           COUNT(*) AS n,
           ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM vehicle_snapshots), 1) AS pct
    FROM vehicle_snapshots
    GROUP BY current_status
""")
for row in cur.fetchall():
    print(row)


print()
print("Q3: Active trains per snapshot over time:")
cur.execute("""
    SELECT collected_at, COUNT(*) AS active_trains
    FROM vehicle_snapshots
    GROUP BY collected_at
    ORDER BY collected_at
""")
for row in cur.fetchall():
    print(row)


print()
print("Q4: Average dwell time (seconds) by station:")
cur.execute("""
    SELECT s.name,
           ROUND(AVG(dwell_seconds), 0) AS avg_dwell_sec,
           COUNT(*) AS train_visits
    FROM (
        SELECT vehicle_id, stop_id,
               (julianday(MAX(collected_at)) - julianday(MIN(collected_at))) * 86400 AS dwell_seconds
        FROM vehicle_snapshots
        WHERE current_status = 'STOPPED_AT'
        GROUP BY vehicle_id, stop_id
        HAVING COUNT(*) >= 2
    ) d
    JOIN stops s ON d.stop_id = s.stop_id
    GROUP BY s.name
    ORDER BY avg_dwell_sec DESC
    LIMIT 10
""")
for row in cur.fetchall():
    print(row)


conn.close()