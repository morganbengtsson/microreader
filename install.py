import sqlite3

con = sqlite3.connect('database.db')

con.execute("""CREATE TABLE channel (
id INTEGER PRIMARY KEY,
link char(200) NOT NULL
""")

con.execute("""CREATE TABLE item (
id INTEGER PRIMARY KEY, 
read bool NOT NULL )""")

con.commit()
