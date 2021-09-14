"""task9_in python Script"""

from datetime import datetime
import sqlite3
import csv
import uuid
import sys


def access_database(db_file, query, parameters=()):
    """Accesses database with the query and parameters given"""
    connect = sqlite3.connect(db_file)
    cursor = connect.cursor()
    cursor.execute(query, parameters)
    connect.commit()
    connect.close()


def access_database_with_result(db_file, query, parameters=()):
    """Accesses database and returns results with the query and parameters given"""
    connect = sqlite3.connect(db_file)
    cursor = connect.cursor()
    rows = cursor.execute(query, parameters).fetchall()
    connect.commit()
    connect.close()
    return rows


# name of csv file eg.(task9_in.csv):
FILENAME = sys.argv[1]

commands = []
with open(FILENAME, 'r', newline='') as file:
    reader = csv.reader(file)

    for row in reader:
        commands.append(row)


# Creates a users:magic combination
usersMagic = {}
for command in commands:

    userID = access_database_with_result("task9_database.db", "SELECT userID FROM loginCredentials \
                                                            WHERE username=?", (command[0],))[0][0]

    TIME = command[1] + '00'
    TIME = str(datetime.strptime(TIME, "%Y%m%d%H%M%S")).replace('-', '/')

    if userID not in usersMagic:
        SESSION_ID = int(str(uuid.uuid4().int)[:10])
        usersMagic[userID] = SESSION_ID

    if command[2] == 'login':

        # Logs in the user
        access_database("task9_database.db", "INSERT INTO sessions (userID, sessionID, loginTime) \
        VALUES (?,?,?)", (userID, usersMagic[userID], TIME))

    elif command[2] == 'logout':
        # Logs out the user
        access_database("task9_database.db", "UPDATE sessions SET logoutTime=? WHERE userID=? \
        AND sessionID=?", (TIME, userID, usersMagic[userID]))

        # Deletes from dictionary when the user logs out
        del usersMagic[userID]

print('database Updated!')
