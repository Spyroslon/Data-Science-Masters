"""task9_out python Script"""

from datetime import datetime, timedelta
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


# Date in the format yyyymmdd
# Padding with 000000 to fill entries for hours:minutes:seconds to match format in table
SPECIFIED_DATE = sys.argv[1] + '000000'

assert len(SPECIFIED_DATE) == 14, 'Invalid Start Date Entry!'

try:
    SPECIFIED_DATE = datetime.strptime(SPECIFIED_DATE, "%Y%m%d%H%M%S")
except ValueError:
    print("Invalid Start Date Entry!")
    sys.exit(-1)

END_OF_SPECIFIED_DATE = SPECIFIED_DATE + timedelta(hours=23, minutes=59, seconds=59)

WEEK_AGO_SPECIFIED_DATE = SPECIFIED_DATE - timedelta(days=6)


# Reference
# https://www.kite.com/python/answers/how-to-get-a-datetime-representing-one-month-ago-in-python
if SPECIFIED_DATE.month == 1:
    MONTH_AGO_SPECIFIED_DATE = SPECIFIED_DATE.replace(year=SPECIFIED_DATE.year - 1,
                                                      month=12, day=SPECIFIED_DATE.day + 1)
else:
    EXTRA_DAYS = 0
    while True:
        try:
            MONTH_AGO_SPECIFIED_DATE = SPECIFIED_DATE.replace(month=SPECIFIED_DATE.month - 1,
                                                              day=SPECIFIED_DATE.day+1 - EXTRA_DAYS)
            break
        except ValueError:
            EXTRA_DAYS += 1

# Creating the dates that will be used as ranges
SPECIFIED_DATE = str(SPECIFIED_DATE).replace('-', '/')
END_OF_SPECIFIED_DATE = str(END_OF_SPECIFIED_DATE).replace('-', '/')
WEEK_AGO_SPECIFIED_DATE = str(WEEK_AGO_SPECIFIED_DATE).replace('-', '/')
MONTH_AGO_SPECIFIED_DATE = str(MONTH_AGO_SPECIFIED_DATE).replace('-', '/')

# Getting the daily, weekly and monthly results
dailyResults = access_database_with_result("task9_database.db", "SELECT * FROM sessions \
WHERE loginTime >= ? AND logoutTime <= ?", (SPECIFIED_DATE, END_OF_SPECIFIED_DATE))


weeklyResults = access_database_with_result("task9_database.db", "SELECT * FROM sessions \
WHERE loginTime >= ? AND logoutTime <= ?", (WEEK_AGO_SPECIFIED_DATE, END_OF_SPECIFIED_DATE))


monthlyResults = access_database_with_result("task9_database.db", "SELECT * FROM sessions \
WHERE loginTime >= ? AND logoutTime <= ?", (MONTH_AGO_SPECIFIED_DATE, END_OF_SPECIFIED_DATE))

# Storing the results in the format {user:[hoursDaily, hoursWeekly, hoursMonthly], ..}
user_hour_results_dict = {}

for result in dailyResults:
    if result[0] not in user_hour_results_dict:
        user_hour_results_dict[result[0]] = [0, 0, 0]

    start_time = datetime.strptime(result[2], '%Y/%m/%d %H:%M:%S')
    end_time = datetime.strptime(result[3], '%Y/%m/%d %H:%M:%S')

    hourDifference = round((end_time - start_time).total_seconds() / 3600, 1)
    user_hour_results_dict[result[0]][0] += hourDifference

for result in weeklyResults:
    if result[0] not in user_hour_results_dict:
        user_hour_results_dict[result[0]] = [0, 0, 0]

    start_time = datetime.strptime(result[2], '%Y/%m/%d %H:%M:%S')
    end_time = datetime.strptime(result[3], '%Y/%m/%d %H:%M:%S')

    hourDifference = round((end_time - start_time).total_seconds() / 3600, 1)
    # Changing the index to access the correct element of the list
    user_hour_results_dict[result[0]][1] += hourDifference

for result in monthlyResults:
    if result[0] not in user_hour_results_dict:
        user_hour_results_dict[result[0]] = [0, 0, 0]

    start_time = datetime.strptime(result[2], '%Y/%m/%d %H:%M:%S')
    end_time = datetime.strptime(result[3], '%Y/%m/%d %H:%M:%S')

    hourDifference = round((end_time - start_time).total_seconds() / 3600, 1)
    # Changing the index to access the correct element of the list
    user_hour_results_dict[result[0]][2] += hourDifference


# Iterates through the dictionary to store the information
# In a format that its easier to write to the csv file
csv_entries = []
for user in user_hour_results_dict:

    line = list()

    username = access_database_with_result("task9_database.db", "SELECT username \
                                            FROM loginCredentials WHERE userID = ?", (user,))[0][0]

    line.append(username)
    line.extend(user_hour_results_dict[user])

    csv_entries.append(line)


with open('task9_out.csv', 'w', newline='') as file:

    write = csv.writer(file)
    write.writerows(csv_entries)

print("'task9_out.csv' created!")
