#!/usr/bin/env python
"""The server python script which uses the server_database.db"""
# This is a simple web server for a traffic counting application.
# It's your job to extend it by adding the backend functionality to support
# recording the traffic in a SQL database. You will also need to support
# some predefined users and access/session control. You should only
# need to extend this file. The client side code (html, javascript and css)
# is complete and does not require editing or detailed understanding.

# import the various libraries needed
import http.cookies as Cookie  # some cookie handling support
from http.server import BaseHTTPRequestHandler, HTTPServer  # the heavy lifting of the web server
import urllib  # some url parsing support
import base64  # some encoding support
import sqlite3
import hashlib
from datetime import datetime
import uuid


# Load the functions that query the traffic database
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


# This function builds a refill action that allows part of the
# currently loaded page to be replaced.
def build_response_refill(where, what):
    text = "<action>\n"
    text += "<type>refill</type>\n"
    text += "<where>"+where+"</where>\n"
    m = base64.b64encode(bytes(what, 'ascii'))
    text += "<what>"+str(m, 'ascii')+"</what>\n"
    text += "</action>\n"
    return text


# This function builds the page redirection action
# It indicates which page the client should fetch.
# If this action is used, only one instance of it should
# contained in the response and there should be no refill action.
def build_response_redirect(where):
    text = "<action>\n"
    text += "<type>redirect</type>\n"
    text += "<where>"+where+"</where>\n"
    text += "</action>\n"
    return text


# Decide if the combination of user and magic is valid
# To check if user is in current sessions?
def handle_validate(iuser, imagic):

    result = access_database_with_result("server_database.db", "SELECT * FROM activeSessions \
                                                                 WHERE userID=? AND sessionID=?",
                                         (iuser, imagic))

    # If it finds a result it returns true. Else returns false
    return len(result) == 1


# remove the combination of user and magic from the data base, ending the login
def handle_delete_session(iuser, imagic):

    # If a user tries to login on the same browser it logs out the previous user
    # Ending their session and logging their logout time
    access_database("server_database.db", "DELETE FROM activeSessions WHERE userID=? \
                                           AND sessionID=?", (iuser, imagic))

    end_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    access_database("server_database.db", "UPDATE sessions SET logoutTime=? WHERE userID=?",
                    (end_time, iuser))


# A user has supplied a username (parameters['usernameinput'][0])
# and password (parameters['passwordinput'][0]) check if these are
# valid and if so, create a suitable session record in the database
# with a random magic identifier that is returned.
# Return the username, magic identifier and the response action set.
def handle_login_request(iuser, imagic, parameters):

    if handle_validate(iuser, imagic):
        # the user is already logged in, so end the existing session.
        handle_delete_session(iuser, imagic)

    text = "<response>\n"

    # Checks if the user has entered a username and password
    if 'usernameinput' and 'passwordinput' in parameters:

        # Preventing sql injection attacks for task 2
        # https://docs.python.org/2/library/sqlite3.html#cursor-objects
        results = access_database_with_result("server_database.db",
                                              "SELECT * from loginCredentials WHERE username=? \
                                              AND password =?", (parameters['usernameinput'][0],
                    hashlib.sha256(parameters['passwordinput'][0].encode('utf-8')).hexdigest()))

        # Checks that the entered username and password has yielded a result
        if len(results) == 1:

            login_check = access_database_with_result("server_database.db",
                                                      "SELECT * FROM activeSessions WHERE userID=?",
                                                      (results[0][0], ))

            # Checks if user is already logged in
            if len(login_check) == 1:
                text += build_response_refill('message', 'User Already Logged In')
                user = '!'
                magic = ''
            else:
                # Adding the new session
                user = results[0][0]
                magic = int(str(uuid.uuid4().int)[:10])
                access_database("server_database.db", "INSERT INTO activeSessions VALUES (?,?)",
                                (user, magic))

                start_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                access_database("server_database.db", "INSERT INTO sessions \
                (userID, sessionID, loginTime) VALUES (?,?,?)", (user, magic, start_time))

                text += build_response_redirect('/page.html')
                text += build_response_refill('total', '0')

        else:
            text += build_response_refill('message', 'Invalid password')
            user = '!'
            magic = ''
        text += "</response>\n"
    else:
        text += build_response_refill('message', 'Blank Entries')
        user = '!'
        magic = ''
        text += "</response>\n"
    return [user, magic, text]


# The user has requested a vehicle be added to the count
# parameters['locationinput'][0] the location to be recorded
# parameters['occupancyinput'][0] the occupant count to be recorded
# parameters['typeinput'][0] the type to be recorded
# Return the username, magic identifier (these can be empty  strings) and the response action set.
def handle_add_request(iuser, imagic, parameters):
    text = "<response>\n"

    if not handle_validate(iuser, imagic):
        # Invalid sessions redirect to login
        text += build_response_redirect('/index.html')
        user = ''
        magic = ''

    else:  # a valid session so process the addition of the entry.
        user = iuser
        magic = imagic

        # Checks if the user has entered a location
        if 'locationinput' not in parameters:
            text += build_response_refill('message', 'Blank location entry')

        else:
            text += build_response_refill('message', 'Entry added.')
            location = parameters['locationinput'][0].lower()
            vehicle_type = parameters['typeinput'][0]
            occupancy = parameters['occupancyinput'][0]

            recording_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            # Records the entry
            access_database("server_database.db", "INSERT INTO traffic \
            (location, vehicleType, occupancy, userID, sessionID, recordedTime) VALUES \
            (?,?,?,?,?,?)", (location, vehicle_type, occupancy, user, magic, recording_time))

            # Updates the total
            total = access_database_with_result("server_database.db", "SELECT COUNT(*) \
            FROM traffic WHERE userID=? AND sessionID=? AND undoFlag IS NULL",
                                                (iuser, imagic))[0][0]
            text += build_response_refill('total', str(total))

    text += "</response>\n"
    return [user, magic, text]


# The user has requested a vehicle be removed from the count
# This is intended to allow counters to correct errors.
# parameters['locationinput'][0] the location to be recorded
# parameters['occupancyinput'][0] the occupant count to be recorded
# parameters['typeinput'][0] the type to be recorded
# Return the username, magic identifier (these can be empty  strings) and the response action set.
def handle_undo_request(iuser, imagic, parameters):
    text = "<response>\n"

    if not handle_validate(iuser, imagic):
        # Invalid sessions redirect to login
        text += build_response_redirect('/index.html')
        user = ''
        magic = ''

    else:  # a valid session so process the recording of the entry.
        user = iuser
        magic = imagic

        # Checks if the user has entered a location
        if 'locationinput' not in parameters:
            text += build_response_refill('message', 'Blank location entry')

        else:
            location = parameters['locationinput'][0].lower()
            vehicle_type = parameters['typeinput'][0]
            occupancy = parameters['occupancyinput'][0]

            result = access_database_with_result("server_database.db",
                                                 "SELECT recordID FROM traffic WHERE location=? \
                                                 AND vehicleType=? AND occupancy=? AND userID=? \
                                                 AND sessionID=? AND undoFlag IS NULL \
                                                 ORDER BY recordID DESC LIMIT 1",
                                                 (location, vehicle_type, occupancy, user, magic))
            # Checks if their is a result with the matching entry
            if len(result) == 1:

                # Updates the undoCheck column with the 'undoed' string
                access_database("server_database.db", "UPDATE traffic \
                SET undoFlag=? WHERE recordID=?", ('undoed', result[0][0]))

                text += build_response_refill('message', 'Entry Un-done.')
            else:
                text += build_response_refill('message', 'No Matching Entry found')

            # Updates the total
            total = access_database_with_result("server_database.db", "SELECT COUNT(*) \
            FROM traffic WHERE userID=? AND sessionID=? AND undoFlag IS NULL", (user, magic))[0][0]
            text += build_response_refill('total', str(total))

    text += "</response>\n"
    return [user, magic, text]


# This code handles the selection of the back button on the record form (page.html)
# You will only need to modify this code if you make changes elsewhere that break its behaviour
def handle_back_request(iuser, imagic, parameters):
    text = "<response>\n"
    if not handle_validate(iuser, imagic):
        text += build_response_redirect('/index.html')
    else:
        text += build_response_redirect('/summary.html')
    text += "</response>\n"
    user = ''
    magic = ''
    return [user, magic, text]


# This code handles the selection of the logout button on the summary page (summary.html)
# You will need to ensure the end of the session is recorded in the database
# And that the session magic is revoked.
def handle_logout_request(iuser, imagic, parameters):

    # Deletes the session and logs the logging out time
    access_database("server_database.db", "DELETE FROM activeSessions WHERE userID=? \
    AND sessionID=?", (iuser, imagic))

    end_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    access_database("server_database.db", "UPDATE sessions SET logoutTime=? WHERE userID=? \
    AND sessionID=?", (end_time, iuser, imagic))

    text = "<response>\n"
    text += build_response_redirect('/index.html')
    user = '!'
    magic = ''
    text += "</response>\n"
    return [user, magic, text]


# This code handles a request for update to the session summary values.
# You will need to extract this information from the database.
def handle_summary_request(iuser, imagic, parameters):
    text = "<response>\n"

    if not handle_validate(iuser, imagic):
        # Invalid sessions redirect to login
        text += build_response_redirect('/index.html')
        user = ''
        magic = ''

    else:
        user = iuser
        magic = imagic
        # Retrieves the sum for each vehicle type for the current user/magic
        sum_car = access_database_with_result("server_database.db", "SELECT COUNT(*) \
        FROM traffic WHERE userID=? AND sessionID=? AND vehicleType=? AND undoFlag IS NULL",
                                              (user, magic, 'car'))[0][0]
        text += build_response_refill('sum_car', str(sum_car))

        sum_taxi = access_database_with_result("server_database.db", "SELECT COUNT(*) \
        FROM traffic WHERE userID=? AND sessionID=? AND vehicleType=? AND undoFlag IS NULL",
                                              (user, magic, 'taxi'))[0][0]
        text += build_response_refill('sum_taxi', str(sum_taxi))

        sum_bus = access_database_with_result("server_database.db", "SELECT COUNT(*) \
        FROM traffic WHERE userID=? AND sessionID=? AND vehicleType=? AND undoFlag IS NULL",
                                              (user, magic, 'bus'))[0][0]
        text += build_response_refill('sum_bus', str(sum_bus))

        sum_motorbike = access_database_with_result("server_database.db", "SELECT COUNT(*) \
        FROM traffic WHERE userID=? AND sessionID=? AND vehicleType=? AND undoFlag IS NULL",
                                              (user, magic, 'motorbike'))[0][0]
        text += build_response_refill('sum_motorbike', str(sum_motorbike))

        sum_bicycle = access_database_with_result("server_database.db", "SELECT COUNT(*) \
        FROM traffic WHERE userID=? AND sessionID=? AND vehicleType=? AND undoFlag IS NULL",
                                              (user, magic, 'bicycle'))[0][0]
        text += build_response_refill('sum_bicycle', str(sum_bicycle))

        sum_van = access_database_with_result("server_database.db", "SELECT COUNT(*) \
        FROM traffic WHERE userID=? AND sessionID=? AND vehicleType=? AND undoFlag IS NULL",
                                              (user, magic, 'van'))[0][0]
        text += build_response_refill('sum_van', str(sum_van))

        sum_truck = access_database_with_result("server_database.db", "SELECT COUNT(*) \
        FROM traffic WHERE userID=? AND sessionID=? AND vehicleType=? AND undoFlag IS NULL",
                                              (user, magic, 'truck'))[0][0]
        text += build_response_refill('sum_truck', str(sum_truck))

        sum_other = access_database_with_result("server_database.db", "SELECT COUNT(*) \
        FROM traffic WHERE userID=? AND sessionID=? AND vehicleType=? AND undoFlag IS NULL",
                                              (user, magic, 'other'))[0][0]
        text += build_response_refill('sum_other', str(sum_other))

        # Finding the total sum
        sum_total = sum_car + sum_taxi + sum_bus + sum_motorbike + sum_bicycle + \
                    sum_van + sum_truck + sum_other
        text += build_response_refill('total', str(sum_total))

    text += "</response>\n"
    return [user, magic, text]


# HTTPRequestHandler class
class myHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    # GET This function responds to GET requests to the web server.
    def do_GET(self):

        # The set_cookies function adds/updates two cookies returned with a webpage.
        # These identify the user who is logged in. The first parameter identifies the user
        # and the second should be used to verify the login session.
        def set_cookies(x, user, magic):
            ucookie = Cookie.SimpleCookie()
            ucookie['u_cookie'] = user
            x.send_header("Set-Cookie", ucookie.output(header='', sep=''))
            mcookie = Cookie.SimpleCookie()
            mcookie['m_cookie'] = magic
            x.send_header("Set-Cookie", mcookie.output(header='', sep=''))

        # The get_cookies function returns the values of the user and magic cookies if they exist
        # it returns empty strings if they do not.
        def get_cookies(source):
            rcookies = Cookie.SimpleCookie(source.headers.get('Cookie'))
            user = ''
            magic = ''
            for keyc, valuec in rcookies.items():
                if keyc == 'u_cookie':
                    user = valuec.value
                if keyc == 'm_cookie':
                    magic = valuec.value
            return [user, magic]

        # Fetch the cookies that arrived with the GET request
        # The identify the user session.
        user_magic = get_cookies(self)

        print(user_magic)

        # Parse the GET request to identify the file requested and the GET parameters
        parsed_path = urllib.parse.urlparse(self.path)

        # Decided what to do based on the file requested.

        # Return a CSS (Cascading Style Sheet) file.
        # These tell the web client how the page should appear.
        if self.path.startswith('/css'):
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('.'+self.path, 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # Return a Javascript file.
        # These tell contain code that the web client can execute.
        if self.path.startswith('/js'):
            self.send_response(200)
            self.send_header('Content-type', 'text/js')
            self.end_headers()
            with open('.'+self.path, 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # A special case of '/' means return the index.html (homepage)
        # of a website
        elif parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('./index.html', 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # Return html pages.
        elif parsed_path.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('.'+parsed_path.path, 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # The special file 'action' is not a real file, it indicates an action
        # we wish the server to execute.
        elif parsed_path.path == '/action':
            self.send_response(200) #respond that this is a valid page request
            # extract the parameters from the GET request.
            # These are passed to the handlers.
            parameters = urllib.parse.parse_qs(parsed_path.query)

            if 'command' in parameters:
                # check if one of the parameters was 'command'
                # If it is, identify which command and call the appropriate handler function.
                if parameters['command'][0] == 'login':
                    [user, magic, text] = handle_login_request(user_magic[0], user_magic[1], parameters)
                    #The result to a login attempt will be to set
                    #the cookies to identify the session.
                    set_cookies(self, user, magic)
                elif parameters['command'][0] == 'add':
                    [user, magic, text] = handle_add_request(user_magic[0], user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'undo':
                    [user, magic, text] = handle_undo_request(user_magic[0], user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'back':
                    [user, magic, text] = handle_back_request(user_magic[0], user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'summary':
                    [user, magic, text] = handle_summary_request(user_magic[0], user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'logout':
                    [user, magic, text] = handle_logout_request(user_magic[0], user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                else:
                    # The command was not recognised, report that to the user.
                    text = "<response>\n"
                    text += build_response_refill('message', 'Internal Error: Command not recognised.')
                    text += "</response>\n"

            else:
                # There was no command present, report that to the user.
                text = "<response>\n"
                text += build_response_refill('message', 'Internal Error: Command not found.')
                text += "</response>\n"
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            self.wfile.write(bytes(text, 'utf-8'))
        else:
            # A file that does n't fit one of the patterns above was requested.
            self.send_response(404)
            self.end_headers()
        return


# This is the entry point function to this code.
def run():
    print('starting server...')
    # You can add any extra start up code here
    # Server settings
    # Choose port 8081 over port 80, which is normally used for a http server
    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address, myHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever() # This function will not return till the server is aborted.


run()
