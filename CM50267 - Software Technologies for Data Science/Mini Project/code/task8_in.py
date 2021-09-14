"""task8_in python Script"""

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


# eg.(task8_in.csv)
FILENAME = sys.argv[1]

commands = []
with open(FILENAME, 'r', newline='') as file:
    reader = csv.reader(file)

    for row in reader:
        commands.append(row)


# "SQLite uses what it calls a dynamic typing system, which ultimately
# means that you can store text in integer fields"
# References
# https://dba.stackexchange.com/questions/106364/text-string-stored-in-sqlite-integer-column
# https://sqlite.org/datatype3.html
# Thus assigning USER to a text value rather than integer will not cause any issues
USER = 'Offline User'
# Assigns a magic to the offline user
SESSION_ID = int(str(uuid.uuid4().int)[:10])

# Iterates though the row of the csv
for command in commands:
    TIME = command[0] + '00'
    TIME = str(datetime.strptime(TIME, "%Y%m%d%H%M%S")).replace('-', '/')

    location = command[2]
    vehicleType = command[3]
    occupancy = command[4]

    if command[1] == 'add':
        # Adding the traffic entries
        access_database("task8_database.db",
                        "INSERT INTO traffic \
                        (location, vehicleType, occupancy, userID, sessionID, recordedTime) \
                        VALUES (?,?,?,?,?,?)",
                        (location, vehicleType, occupancy, USER, SESSION_ID, TIME))

    elif command[1] == 'undo':
        # Or undoing the traffic entries
        result = access_database_with_result("task8_database.db", "SELECT recordID FROM traffic \
        WHERE location=? AND vehicleType=? AND occupancy=? AND userID=? AND sessionID=? \
        AND undoFlag IS NULL ORDER BY recordID DESC LIMIT 1",
                                             (location, vehicleType, occupancy, USER, SESSION_ID))

        # But first checking if a matching entry was found
        if len(result) == 1:
            access_database("task8_database.db", "UPDATE traffic SET undoFlag=? \
            WHERE recordID=?", ('undoed', result[0][0]))

print('database Updated!')
