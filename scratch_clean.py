import sqlite3

conn = sqlite3.connect("war_remnants_museum.db")
cur = conn.cursor()
cur.execute("DELETE FROM exhibit WHERE code = 'TEST-01'")
cur.execute("DELETE FROM content_source WHERE exhibit_id NOT IN (SELECT id FROM exhibit)")
conn.commit()

cur.execute("SELECT code FROM exhibit")
codes = [r[0] for r in cur.fetchall()]
print("Current exhibits in DB:", codes)
conn.close()
