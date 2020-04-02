# This File is for setting up Sqlite3 database
import sqlite3

conn = sqlite3.connect('finance.db')
cur = conn.cursor()

# Execute following Sqlite script
cur.executescript('''
CREATE TABLE 'transactions' 
    ('id' integer PRIMARY KEY AUTOINCREMENT NOT NULL, 
    'createdate' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    'type' char(4) NOT NULL, 
    'user_id' integer NOT NULL, 
    'symbol' char(8) NOT NULL, 
    'shares' integer NOT NULL, 
    'price' numeric(10,4) NOT NULL);

CREATE TABLE 'users' 
    ('id' integer PRIMARY KEY AUTOINCREMENT NOT NULL, 
    'username' text NOT NULL, 
    'hash' text NOT NULL, 
    'cash' numeric(10, 4) NOT NULL DEFAULT 10000 );

CREATE UNIQUE INDEX 'username' ON "users" ("username");
''')