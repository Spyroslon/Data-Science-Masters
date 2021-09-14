import sqlite3
import hashlib


def access_database(db_file, query, parameters=()):
    """Accesses database with the query and parameters given"""
    connect = sqlite3.connect(db_file)
    cursor = connect.cursor()
    cursor.execute(query, parameters)
    connect.commit()
    connect.close()


def setup_traffic_tables(db_file):
    # Get rid of any existing data
    access_database(db_file, "DROP TABLE IF EXISTS loginCredentials")
    access_database(db_file, "DROP TABLE IF EXISTS activeSessions")
    access_database(db_file, "DROP TABLE IF EXISTS sessions")
    access_database(db_file, "DROP TABLE IF EXISTS traffic")

    # Freshly setup tables
    access_database(db_file, "CREATE TABLE loginCredentials (userID INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL)")
    access_database(db_file, "CREATE TABLE activeSessions (userID INTEGER UNIQUE NOT NULL, sessionID INTEGER UNIQUE NOT NULL)")
    access_database(db_file, "CREATE TABLE sessions (userID INTEGER NOT NULL, sessionID INTEGER UNIQUE NOT NULL, loginTime TEXT NOT NULL, logoutTime TEXT)")
    access_database(db_file, "CREATE TABLE traffic (location TEXT NOT NULL, vehicleType TEXT NOT NULL, occupancy INTEGER NOT NULL, userID INTEGER NOT NULL, sessionID INTEGER NOT NULL, recordedTime TEXT NOT NULL, undoFlag TEXT, recordID INTEGER PRIMARY KEY AUTOINCREMENT)")

    # Populate the tables with some initial data
    access_database(db_file, "INSERT INTO loginCredentials (username, password) VALUES (?,?)", ('test1', str(hashlib.sha256(b'password1').hexdigest())))
    access_database(db_file, "INSERT INTO loginCredentials (username, password) VALUES (?,?)", ('test2', str(hashlib.sha256(b'password2').hexdigest())))
    access_database(db_file, "INSERT INTO loginCredentials (username, password) VALUES (?,?)", ('test3', str(hashlib.sha256(b'password3').hexdigest())))
    access_database(db_file, "INSERT INTO loginCredentials (username, password) VALUES (?,?)", ('test4', str(hashlib.sha256(b'password4').hexdigest())))
    access_database(db_file, "INSERT INTO loginCredentials (username, password) VALUES (?,?)", ('test5', str(hashlib.sha256(b'password5').hexdigest())))
    access_database(db_file, "INSERT INTO loginCredentials (username, password) VALUES (?,?)", ('test6', str(hashlib.sha256(b'password6').hexdigest())))
    access_database(db_file, "INSERT INTO loginCredentials (username, password) VALUES (?,?)", ('test7', str(hashlib.sha256(b'password7').hexdigest())))
    access_database(db_file, "INSERT INTO loginCredentials (username, password) VALUES (?,?)", ('test8', str(hashlib.sha256(b'password8').hexdigest())))
    access_database(db_file, "INSERT INTO loginCredentials (username, password) VALUES (?,?)", ('test9', str(hashlib.sha256(b'password9').hexdigest())))
    access_database(db_file, "INSERT INTO loginCredentials (username, password) VALUES (?,?)", ('test10', str(hashlib.sha256(b'password10').hexdigest())))


# Un-comment a line and run to clear the appropriate database that will be used in the different tasks
setup_traffic_tables("initial_database.db")
# setup_traffic_tables("server_database.db")
# setup_traffic_tables("task8_database.db")
# setup_traffic_tables("task9_database.db")

