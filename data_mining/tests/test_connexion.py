import sqlite3

conn = sqlite3.connect('db.sqlite3')
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables disponibles :")
for t in tables:
    print(" -", t[0])
conn.close()