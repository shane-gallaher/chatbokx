import sqlite3

conn = sqlite3.connect("chatbox.db")
next_id=""
data = conn.execute("select count(id) from tbl_chats;")
for row in data:
    next_id=int(row[0])
print(next_id)
conn.close()