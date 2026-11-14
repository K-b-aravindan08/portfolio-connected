import sqlite3

conn = sqlite3.connect('portfolio.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM messages')
count = cursor.fetchone()[0]
print(f"Total messages: {count}")

cursor.execute('SELECT * FROM messages')
for msg in cursor.fetchall():
    print(msg)