import os
import json
import sqlite3 as sql

from dota import api

with open(os.path.expanduser('~/Dropbox/bin/api-keys.txt'), 'r') as f:
    api_keys = json.load(f)

KEY = api_keys['steam']  # just a string with the key.

h = api.API(KEY)
hist = h.get_match_history()
d = hist.get_all_match_details()

conn = sql.connect('dota.db')

with conn:

    c = conn.cursor()
    c.execute("CREATE TABLE Matches(p1 INT, p2 INT, p3 INT, p4 INT, p5 INT, p6 INT, p7 INT, p8 INT, p9 INT, p10 INT)")
    
