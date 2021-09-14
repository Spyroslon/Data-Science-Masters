"""task8_out python Script"""

from datetime import datetime
import sqlite3
import csv
import sys


def access_database_with_result(db_file, query, parameters=()):
    """Accesses database and returns results with the query and parameters given"""
    connect = sqlite3.connect(db_file)
    cursor = connect.cursor()
    rows = cursor.execute(query, parameters).fetchall()
    connect.commit()
    connect.close()
    return rows


# Start Date in the format (yyyymmddhhmm)
# Padding with 00 to fill entries for seconds to match format in table
START_DATE = sys.argv[1] + '00'

assert len(START_DATE) == 14, 'Invalid Start Date Entry!'

# Checks if the entered start date is valid
try:
    START_DATE = str(datetime.strptime(START_DATE, "%Y%m%d%H%M%S")).replace('-', '/')
except ValueError:
    print("Invalid Start Date Entry!")
    sys.exit(-1)

# End Date in the format (yyyymmddhhmm)
# Padding with 00 to fill entries for seconds to match format in table
END_DATE = sys.argv[2] + '00'

assert len(END_DATE) == 14, 'Invalid End Date Entry!'

# Checks if the entered end date is valid
try:
    END_DATE = str(datetime.strptime(END_DATE, "%Y%m%d%H%M%S")).replace('-', '/')
except ValueError:
    print("Invalid End Date Entry!")
    sys.exit(-1)

traffic_results = access_database_with_result("task8_database.db", "SELECT * FROM traffic \
WHERE undoFlag IS NULL AND recordedTime BETWEEN ? AND ?", (START_DATE, END_DATE))

# Checks if at least some results where found
if len(traffic_results) == 0:
    print('No results found for entries added!')

dict_entries = {}

# Loops through the results to create a dictionary in the format
# {location:type:[count(occ1),count(occ2),count(occ3),count(occ4)], ..}
for result in traffic_results:

    # Check Location, if location is not in the dictionary add it
    if result[0] not in dict_entries:
        dict_entries[result[0]] = {}
        dict_entries[result[0]][result[1]] = [0, 0, 0, 0]
        dict_entries[result[0]][result[1]][result[2] - 1] += 1

    # If location is in the dictionary and the car type is not in the dictionary add the car type
    elif result[1] not in dict_entries[result[0]]:

        dict_entries[result[0]][result[1]] = [0, 0, 0, 0]
        dict_entries[result[0]][result[1]][result[2] - 1] += 1

    else:
        dict_entries[result[0]][result[1]][result[2] - 1] += 1


csv_entries = []
# Iterates through the dictionary to store the information
# In a format that its easier to write to the csv file
for location in dict_entries:

    for vehicleType in dict_entries[location].keys():

        line = list()

        line.append(location)
        line.append(vehicleType)
        line.extend(dict_entries[location][vehicleType])

        csv_entries.append(line)


with open('task8_out.csv', 'w', newline='') as file:

    write = csv.writer(file)
    write.writerows(csv_entries)

print("'task8_out.csv' created!")
