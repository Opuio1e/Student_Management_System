import sqlite3
conn = sqlite3.connect('schoolgate.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS log (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 student_id TEXT, 
                 timestamp TEXT,
                 action TEXT)''')
conn.commit()

