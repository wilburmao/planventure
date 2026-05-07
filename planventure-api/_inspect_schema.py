import os
import sqlite3

os.chdir(r'C:\Users\wilbu\Documents\planventure\planventure\planventure-api')
conn = sqlite3.connect('planventure.db')
c = conn.cursor()
c.execute('PRAGMA table_info(trips)')
print(c.fetchall())
conn.close()
