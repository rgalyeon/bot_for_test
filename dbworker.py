# -*- coding: utf-8 -*-
import sqlite3
import config

"""
Functions that help
to work with database
"""



# Function add member and his state to database
def add_states(id, state):
    conn = sqlite3.connect(config.db_file)
    c = conn.cursor()
    c.execute("INSERT INTO states VALUES (:id, :state)",
              {'id': id, 'state': state})
    conn.commit()
    conn.close()

# Function changes state
def update_state(id, state):
    conn = sqlite3.connect(config.db_file)
    c = conn.cursor()
    c.execute("""UPDATE states SET state = :state
                WHERE id = :id""",
              {'id': id, 'state': state})
    conn.commit()
    conn.close()

# Function deletes player's data from database
def remove_id(id):
    conn = sqlite3.connect(config.db_file)
    c = conn.cursor()
    c.execute("DELETE from states WHERE id = :id",
              {'id': id})
    conn.commit()
    conn.close()

# Function get the current state
def get_state(id):
    conn = sqlite3.connect(config.db_file)
    c = conn.cursor()
    c.execute("SELECT * FROM states WHERE id = :id",
              {'id': id})
    try:
        return c.fetchall()[0][1]
    except:
        return 'False'
