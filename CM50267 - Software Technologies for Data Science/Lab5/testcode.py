import sqlite3

# access_database requires the name of a sqlite3 database file and the query.
# It does not return the result of the query.
def access_database(dbfile, query):
    connect = sqlite3.connect(dbfile)
    cursor = connect.cursor()
    cursor.execute(query)
    connect.commit()
    connect.close()

# access_database requires the name of a sqlite3 database file and the query.
# It returns the result of the query
def access_database_with_result(dbfile, query):
    connect = sqlite3.connect(dbfile)
    cursor = connect.cursor()
    rows = cursor.execute(query).fetchall()
    connect.commit()
    connect.close()
    return rows


def student_units(database, studentid, year):
    row = access_database_with_result(database, "SELECT unitid FROM enrolled \
                                                WHERE studentid=" + str(studentid) + " \
                                                AND year=" + str(year) + " \
                                                ORDER BY unitid")
    l = []
    for u in row:
        l.append(u[0])
    return l


# %%
# Task 2 (1 Mark): Provide a function that indicates the students that are enrolled on a unit.
# It should return a list of tupples of studentid and name ordered by studentid. e.g. [(110,'Zipppy'),(111,'Bungle')]

def unit_students(database, unitid, year):
    row = access_database_with_result(database, "SELECT students.studentid, students.name \
                                                FROM enrolled, students \
                                                WHERE enrolled.studentid=students.studentid \
                                                AND enrolled.unitid=" + str(unitid) + " \
                                                AND enrolled.year=" + str(year))
    return row


# %%
# Task 3 (1 Marks): Provide a function that indicates how many students are taking each unit in a given year.
# It should return a list of tupples of unitid, unitname and count ordered by sunitid. e.g. [(1010,'Machine Learning',50),(1020,'Dissertaton',37)]

def unit_numbers(database, year):
    row = access_database_with_result(database,
                                      "SELECT units.unitid, units.name, count(enrolled.studentid) FROM units,enrolled WHERE enrolled.unitid=units.unitid AND enrolled.year = " + str(
                                          year) + " GROUP BY units.unitid ORDER BY units.unitid")
    return row


# %%
# Task 4 (2 Marks): Provide a function that uses the enrollments and assessements tables to fully populate the assignments table.
# All asssignemnts for each student in a given year should be created. Only the assignements a student should be
# undertaking should be created.

def create_assignments(database, year):
    rows = access_database_with_result(database, "INSERT INTO assignments (studentid, assessmentid, deadline, marked) \
                                                 SELECT enrolled.studentid, assessments.assessmentid, assessments.deadline, 0 \
                                                 FROM enrolled INNER JOIN assessments  \
                                                 ON enrolled.unitid = assessments.unitid \
                                                 WHERE assessments.year=" + str(year) + " \
                                                 AND enrolled.year=" + str(year))


# %%
# Task 5 (1 Mark): Update the mark of an assignment, given the studentid, assessmentid and mark.
# It should update the marked flag and the mark.

def mark_assignment(database, studentid, assessmentid, mark):
    access_database(database, "UPDATE assignments \
                              SET mark=" + str(mark) + " , marked=" + str(1) + "\
                              WHERE studentid=" + str(studentid) + "\
                              AND assessmentid=" + str(assessmentid))


# %%
# Task 6 (2 Marks): Compute the overall mark for all students taking a specified unit in a given year.

def unit_marks(database, unitid, year):
    rows = access_database_with_result(database, "SELECT assignments.studentid, ROUND(assignments.mark * assessments.weighting / assessments.mark , 2) \
                                                 FROM assessments, assignments \
                                                 WHERE assessments.year=" + str(year) + "\
                                                 AND assessments.unitid=" + str(unitid) + "\
                                                 AND assessments.assessmentid = assignments.assessmentid")
    return rows


# %%
# Task 7 (2 Marks): Compute the overall marks for each unit taken by a given student across all years.

def student_marks(database, studentid):
    rows = access_database_with_result(database, "SELECT assessments.unitid, assessments.year ,ROUND(SUM(assignments.mark * assessments.weighting), 2) / assessments.mark \
                                                 FROM assessments, assignments \
                                                 WHERE assignments.studentid=" + str(studentid) + "\
                                                 AND assessments.assessmentid = assignments.assessmentid \
                                                 GROUP BY assessments.unitid")
    return rows

# --------------------------------------------------

def setup_assessment_tables2(dbfile):
    # Get rid of any existing data
    access_database(dbfile, "DROP TABLE IF EXISTS units")
    access_database(dbfile, "DROP TABLE IF EXISTS students")
    access_database(dbfile, "DROP TABLE IF EXISTS enrolled")
    access_database(dbfile, "DROP TABLE IF EXISTS assessments")
    access_database(dbfile, "DROP TABLE IF EXISTS assignments")
    # Freshly setup tables
    access_database(dbfile, "CREATE TABLE units (unitid INT, name TEXT, level INT, semester INT)")
    access_database(dbfile, "CREATE TABLE students (studentid INT, name TEXT)")
    access_database(dbfile, "CREATE TABLE enrolled (studentid INT, unitid INT, year INT)")
    access_database(dbfile, "CREATE TABLE assessments (assessmentid INT, unitid INT, year INT, name TEXT, mark INT, weighting INT, deadline DATE)")
    access_database(dbfile, "CREATE TABLE assignments (assignmentid INTEGER PRIMARY KEY AUTOINCREMENT, studentid INT, assessmentid INT, deadline DATE, submitted DATE, mark INT, marked INT)")
    # Populate the tables with some initial data
    access_database(dbfile, "INSERT INTO units VALUES (200,'ZERO', 6, 1), (201,'ONE', 6, 1), (202,'TWO', 6, 1)")
    access_database(dbfile, "INSERT INTO students VALUES (2001,'Rod'),(2002,'Jane'),(2003,'Freddy')")
    access_database(dbfile,"INSERT INTO enrolled VALUES (2001,201,2020), (2001,202,2019), (2002,200,2020), (2002,201,2020), (2002,202,2020), (2003,200,2020), (2003, 201, 2019), (2003, 202, 2020)")
    access_database(dbfile,"INSERT INTO assessments VALUES (1,200,2020,'Exam',60,75,'2021-1-25 20:00'),(2,200,2020,'Coursework',100,25,'2020-12-25 20:00'),(3,201,2020,'Coursework',60,100,'2020-12-15 20:00'),(4,202,2020,'Coursework',50,100,'2019-12-15 20:00'),(5,202,2019,'Coursework',40,100,'2019-12-15 20:00')")

def setup_part2_tables(dbfile,year):
    setup_assessment_tables2(dbfile)
    access_database(dbfile,"INSERT INTO assignments (assignmentid, studentid, assessmentid, deadline, submitted, mark, marked) SELECT NULL, enrolled.studentid, assessments.assessmentid, assessments.deadline, NULL, NULL,0 FROM enrolled,assessments WHERE assessments.unitid=enrolled.unitid AND assessments.year=enrolled.year AND assessments.year="+str(year))

def mark2_assignment(database, studentid, assessmentid, mark):
    access_database(database,"UPDATE assignments SET marked = 1, mark = "+str(mark)+" WHERE assessmentid = "+str(assessmentid)+" AND studentid = "+str(studentid))

def run_tests2(who):
    print("Start "+str(who))
    reason = ""
    try:
        setup_assessment_tables2("example.db")
    except:
        print("Exception Raised Setup")

# task 1 (1)
    try:
        result1 = student_units("example.db",2001,2020)
        print(result1)
        if len(result1) == 1:
           if result1[0] == 201:
               mark1 = 1
           else:
               mark1 = 0
               reason = reason + "Task 1: Test returned wrong number of entries. "
        else:
            mark1 = 0
            reason = reason + "Task 1: Test returned unexpected value. "
    except:
        mark1 = 0
        reason = reason + "Task 1: Test raised exception. "
        print("Exception Raised 1")

# task 2 (1)
    try:
        result2 = unit_students("example.db",201,2020)
        print(result2)
        if len(result2) == 2:
            if result2[0][0] == 2001 and result2[1][0] == 2002:
                mark2 = 1 
            else:
                mark2 = 0;
                reason = reason + "Task 2: Test returned unexpected values. "
        else:
          reason = reason + "Task 2: Test returned wrong number of entries. "
          mark2 = 1
    except:
        mark2 = 0
        reason = reason + "Task 2: Test raised exception. "
        print("Exception Raised 2")

#task 3 (1) code provided
    try:
        result3 = unit_numbers("example.db",2020)
        print(result3)
        # no point testing, they were given the code by mistake
        mark3 = 1
    except:
        mark3 = 0
        reason = reason + "Task 3: Test raised exception. "
        print("Exception Raised 3")

#task 4 (2)
    try:
        create_assignments("example.db",2020)
        result4 = access_database_with_result("example.db","SELECT COUNT(*) FROM assignments;")
        print(result4)
        if result4[0][0] == 8:
            mark4 = 2
        else:
            reason = reason + "Task 4: Wrong number of rows added. "
            mark4 = 0;
    except:
        mark4 = 0
        reason = reason + "Task 4: Test raised exception. "
        print("Exception Raised 4")

# reset database to good state
    setup_part2_tables("example.db",2020)

#task 5 (1)
    try:
        mark_assignment("example.db",2001, 3,30)
        mark_assignment("example.db",2002, 1,40)
        mark_assignment("example.db",2002, 2,100)
        mark_assignment("example.db",2002, 3,45)
        mark_assignment("example.db",2002, 4,25)
        mark_assignment("example.db",2003, 1,60)
        mark_assignment("example.db",2003, 2,80)
        mark_assignment("example.db",2003, 4,50)
        result5 = access_database_with_result("example.db","SELECT SUM(mark) FROM assignments;")
        print(result5) #430
        if result5[0][0] == 430:
            mark5 = 1
        else:
            reason = reason + "Task 5: Marks recorded not expected value. "
            mark5 = 0;
    except:
        mark5 = 0
        reason = reason + "Task 5: Test raised exception. "
        print("Exception Raised 5")

# reset database to good state
    setup_part2_tables("example.db",2020)
    mark2_assignment("example.db",2001, 3,30)
    mark2_assignment("example.db",2002, 1,40)
    mark2_assignment("example.db",2002, 2,100)
    mark2_assignment("example.db",2002, 3,45)
    mark2_assignment("example.db",2002, 4,25)
    mark2_assignment("example.db",2003, 1,60)
    mark2_assignment("example.db",2003, 2,80)
    mark2_assignment("example.db",2003, 4,50)


#task 6 (2)
    try:
        result6 = unit_marks("example.db", 200, 2020)
        print('6 >>',result6)
        if len(result6) == 2:
            if len(result6[0]) == 2:
                if result6[0][0]==2002 and result6[0][1] == 75 and result6[1][0]==2003 and result6[1][1] == 95:
                    mark6 = 2
                elif result6[1][0]==2002 and result6[1][1] == 75 and result6[0][0]==2003 and result6[0][1] == 95:
                    mark6 = 2
                else:
                    mark6 = 0
                    reason = reason + "Task 6: Not expected values. "
            else:
                mark6 = 0
                reason = reason + "Task 6: Not expected number of parameters in results. "
        else:
            mark6 = 0
            reason = reason + "Task 6: Not expected number of results. "
    except:
        mark6 = 0
        reason = reason + "Task 6: Test raised exception. "
        print("Exception Raised 6")

#task 7 (2)
    try:
        result7 = student_marks("example.db",2002)
        print(result7)
        if len(result7) == 3:
          if len(result7[0]) == 3:
              unitsum = result7[0][0] + result7[1][0] + result7[2][0];
              yearsum = result7[0][1] + result7[1][1] + result7[2][1];
              marksum = result7[0][2] + result7[1][2] + result7[2][2];
              if unitsum == 603 and yearsum == 6060 and marksum == 200:
                  mark7 = 2
              else:
                  mark7 = 0
                  reason = reason + "Task 7: Not expected values. "
          else:
              mark7 = 0
              reason = reason + "Task 7: Not expected number of parameters in results. "
        else:
            mark7 = 0
            reason = reason + "Task 7: Not expected number of results. "
    except:
        mark7 = 0
        reason = reason + "Task 7: Test raised exception. "
        print("Exception Raised 7")

    print("End "+str(who))
    marks = mark1+mark2+mark3+mark4+mark5+mark6+mark7
    if reason == '':
        reason="Well done."
    print("Participant "+str(who)+","+str(mark1)+","+str(mark2)+","+str(mark3)+","+str(mark4)+","+str(mark5)+","+str(mark6)+","+str(mark7)+","+str(marks)+","+reason)


run_tests2('Spyros')