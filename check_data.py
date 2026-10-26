import sqlite3

conn = sqlite3.connect("mbta.db")
cur = conn.cursor()

# Question 1: how many rows do we have in total?
cur.execute("SELECT COUNT(*) FROM vehicle_snapshots")
print("Total rows:", cur.fetchone()[0])

# Question 2: how many trains are in each status?
cur.execute("""
    SELECT current_status, COUNT(*)
    FROM vehicle_snapshots
    GROUP BY current_status
""")
for row in cur.fetchall():
    print(row)

# Question 3: how many snapshots have we collected so far?
cur.execute("SELECT COUNT(DISTINCT collected_at) FROM vehicle_snapshots")
print("Snapshots collected:", cur.fetchone()[0])

conn.close()