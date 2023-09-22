from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, send_file, session,  jsonify, json
from pymysql import connections, cursors
import os
import boto3
from config import *
from io import BytesIO
import cv2
import pytesseract

app = Flask(__name__)
app.config["SECRET_KEY"] = "sem-sk"
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)
output = {}

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('Index.html')

@app.route("/programme", methods=['GET', 'POST'])
def Get_Programme():
    if request.method == 'GET':
        cursor = db_conn.cursor()
        query = "SELECT * FROM Programme ORDER BY programmeDuration"
        cursor.execute(query)
        prog = cursor.fetchall()
        print(prog[0])
        cursor.close()
        return render_template('Programme.html', prog=prog)
    
@app.route("/progDetails/<progID>", methods=['GET', 'POST'])
def Get_Programme_Details(progID):
    if request.method == 'GET':        
        cursor = db_conn.cursor()
        progSql = "SELECT * FROM Programme WHERE ProgrammeID=%s"
        cursor.execute(progSql,(progID))
        prog = cursor.fetchall()
        courseSql = "SELECT Course.* FROM Course,ProgrammeCourse,Programme WHERE Programme.programmeID = ProgrammeCourse.programmeID AND ProgrammeCourse.courseCode = Course.courseCode AND Programme.programmeID=%s ORDER BY CourseName"
        cursor.execute(courseSql,(progID))
        course = cursor.fetchall()
        reqSql = "SELECT * FROM QualificationSubject WHERE programmeID=%s ORDER BY qualificationName"
        cursor.execute(reqSql,(progID))
        tempReq = cursor.fetchall()
        grouped_data = defaultdict(list)
        progOvSql = "SELECT intakeYear,intakeMonth,programmeDuration,campusName FROM Programme,ProgrammeCampus,Intake,Campus WHERE Programme.programmeID = ProgrammeCampus.programmeID  AND Intake.IntakeID = ProgrammeCampus.intakeID AND Campus.campusID = ProgrammeCampus.campusID AND Programme.programmeID = %s"
        cursor.execute(progOvSql,(progID))        
        ov = cursor.fetchall()
        for row in tempReq:
            group_key = row[3]
            grouped_data[group_key].append(row)
        cursor.close()
        return render_template('ProgDetails.html',progID=progID, prog=prog ,course=course, req=grouped_data,ov=ov)

@app.route("/progCompare/<progID>", methods=['GET', 'POST'])
def Compare_Programme(progID):
    cursor = db_conn.cursor()    
    if request.method == 'GET':
        mainProg = "Select * from Programme WHERE programmeID = %s"
        cursor.execute(mainProg,(progID))
        mProg = cursor.fetchall()
        progListSql = "Select programmeName,programmeID from Programme WHERE programmeID != %s AND programmeType = %s"
        cursor.execute(progListSql,(progID,mProg[0][4]))
        progList = cursor.fetchall()
        #overview1
        progOvSql = "SELECT programmeName, intakeYear,intakeMonth,programmeDuration,campusName FROM Programme,ProgrammeCampus,Intake,Campus WHERE Programme.programmeID = ProgrammeCampus.programmeID  AND Intake.IntakeID = ProgrammeCampus.intakeID AND Campus.campusID = ProgrammeCampus.campusID AND Programme.programmeID = %s"
        cursor.execute(progOvSql,(progID))
        mOv = cursor.fetchall()
        progDict = {}
        for prog in mOv:
            if prog[0] not in progDict:
                progDict[prog[0]] = {'intake': [], 'locations': []}
            progDict[prog[0]]['intake'].append(f"{prog[1]}/{prog[2]}")

            progDict[prog[0]]['locations'].append(prog[4])
            progDict[prog[0]]['duration'] = prog[3]
        progDict[mOv[0][0]]['intake'] = set(progDict[mOv[0][0]]['intake'])
        progDict[mOv[0][0]]['locations'] = set(progDict[mOv[0][0]]['locations'])
        
        #overview2
        progOvSql = "SELECT programmeName, intakeYear,intakeMonth,programmeDuration,campusName FROM Programme,ProgrammeCampus,Intake,Campus WHERE Programme.programmeID = ProgrammeCampus.programmeID  AND Intake.IntakeID = ProgrammeCampus.intakeID AND Campus.campusID = ProgrammeCampus.campusID AND Programme.programmeID = %s"
        cursor.execute(progOvSql,(progList[0][1]))
        mOv = cursor.fetchall()
        progDict1 = {}
        for prog in mOv:
            if prog[0] not in progDict1:
                progDict1[prog[0]] = {'intake': [], 'locations': []}
            progDict1[prog[0]]['intake'].append(f"{prog[1]}/{prog[2]}")
            progDict1[prog[0]]['locations'].append(prog[4])
            progDict1[prog[0]]['duration'] = prog[3]
        progDict1[mOv[0][0]]['intake'] = set(progDict1[mOv[0][0]]['intake'])
        progDict1[mOv[0][0]]['locations'] = set(progDict1[mOv[0][0]]['locations'])
        combinedDict = {}
        combinedDict.update(progDict)
        combinedDict.update(progDict1)
        sortedDict = sorted(combinedDict.items(), key=lambda x: x[0])

        #compare requirement
        reqSql = "(SELECT DISTINCT programmeName,qualificationName,subjectName,grade FROM QualificationSubject, Programme WHERE QualificationSubject.programmeID = Programme.programmeID AND Programme.programmeID=%s)UNION(SELECT DISTINCT programmeName,qualificationName,subjectName,grade FROM QualificationSubject, Programme WHERE QualificationSubject.programmeID = Programme.programmeID AND Programme.programmeID=%s)ORDER BY qualificationName"
        cursor.execute(reqSql,(progID,progList[0][1]))
        allReq = cursor.fetchall()
        prog_data = []

        # Iterate over the list of tuples and add the data to the list of dictionaries
        for prog_name, level, subject, grade in allReq:
            prog_data.append({
            "Program": prog_name,
            "Level": level,
            "Subject": subject,
            "Grade": grade
            })
        allCoursesSql = "SELECT courseName FROM Course,Programme,ProgrammeCourse WHERE Programme.programmeID = ProgrammeCourse.programmeID AND ProgrammeCourse.courseCode = Course.courseCode AND Programme.programmeID = %s UNION SELECT courseName FROM Course,Programme,ProgrammeCourse WHERE Programme.programmeID = ProgrammeCourse.programmeID AND ProgrammeCourse.courseCode = Course.courseCode AND Programme.programmeID = %s"
        cursor.execute(allCoursesSql,(progID,progList[0][1]))
        allCourses = cursor.fetchall()

        progNameSql = "Select programmeName from Programme WHERE programmeID=%s"
        cursor.execute(progNameSql,(progList[0][1]))
        cName = cursor.fetchall()
        coursesSql = "SELECT courseName FROM Course,Programme,ProgrammeCourse WHERE Programme.programmeID = ProgrammeCourse.programmeID  AND ProgrammeCourse.courseCode = Course.courseCode AND Programme.programmeID = %s"
        cursor.execute(coursesSql,progID)
        courses1 = cursor.fetchall()
        cursor.execute(coursesSql,(progList[0][1]))
        courses2 = cursor.fetchall()

    if request.method == 'POST':
        cProgID = request.form["cProg"]
        mainProg = "Select * from Programme WHERE programmeID = %s"
        cursor.execute(mainProg,(progID))
        mProg = cursor.fetchall()
        progListSql = "Select programmeName,programmeID from Programme WHERE programmeID != %s AND programmeType = %s"
        cursor.execute(progListSql,(progID,mProg[0][4]))
        progList = cursor.fetchall()
        #overview1
        progOvSql = "SELECT programmeName, intakeYear,intakeMonth,programmeDuration,campusName FROM Programme,ProgrammeCampus,Intake,Campus WHERE Programme.programmeID = ProgrammeCampus.programmeID  AND Intake.IntakeID = ProgrammeCampus.intakeID AND Campus.campusID = ProgrammeCampus.campusID AND Programme.programmeID = %s"
        cursor.execute(progOvSql,(progID))
        mOv = cursor.fetchall()
        progDict = {}
        for prog in mOv:
            if prog[0] not in progDict:
                progDict[prog[0]] = {'intake': [], 'locations': []}
            progDict[prog[0]]['intake'].append(f"{prog[1]}/{prog[2]}")

            progDict[prog[0]]['locations'].append(prog[4])
            progDict[prog[0]]['duration'] = prog[3]
        progDict[mOv[0][0]]['intake'] = set(progDict[mOv[0][0]]['intake'])
        progDict[mOv[0][0]]['locations'] = set(progDict[mOv[0][0]]['locations'])
        
        #overview2
        progOvSql = "SELECT programmeName, intakeYear,intakeMonth,programmeDuration,campusName FROM Programme,ProgrammeCampus,Intake,Campus WHERE Programme.programmeID = ProgrammeCampus.programmeID  AND Intake.IntakeID = ProgrammeCampus.intakeID AND Campus.campusID = ProgrammeCampus.campusID AND Programme.programmeID = %s"
        cursor.execute(progOvSql,(cProgID))
        mOv = cursor.fetchall()
        progDict1 = {}
        for prog in mOv:
            if prog[0] not in progDict1:
                progDict1[prog[0]] = {'intake': [], 'locations': []}
            progDict1[prog[0]]['intake'].append(f"{prog[1]}/{prog[2]}")
            progDict1[prog[0]]['locations'].append(prog[4])
            progDict1[prog[0]]['duration'] = prog[3]
        progDict1[mOv[0][0]]['intake'] = set(progDict1[mOv[0][0]]['intake'])
        progDict1[mOv[0][0]]['locations'] = set(progDict1[mOv[0][0]]['locations'])
        combinedDict = {}
        combinedDict.update(progDict)
        combinedDict.update(progDict1)
        sortedDict = sorted(combinedDict.items(), key=lambda x: x[0])

        #compare requirement
        reqSql = "(SELECT DISTINCT programmeName,qualificationName,subjectName,grade FROM QualificationSubject, Programme WHERE QualificationSubject.programmeID = Programme.programmeID AND Programme.programmeID=%s)UNION(SELECT DISTINCT programmeName,qualificationName,subjectName,grade FROM QualificationSubject, Programme WHERE QualificationSubject.programmeID = Programme.programmeID AND Programme.programmeID=%s)ORDER BY qualificationName"
        cursor.execute(reqSql,(progID,cProgID))
        allReq = cursor.fetchall()
        prog_data = []

        # Iterate over the list of tuples and add the data to the list of dictionaries
        for prog_name, level, subject, grade in allReq:
            prog_data.append({
            "Program": prog_name,
            "Level": level,
            "Subject": subject,
            "Grade": grade
            })
        allCoursesSql = "SELECT courseName FROM Course,Programme,ProgrammeCourse WHERE Programme.programmeID = ProgrammeCourse.programmeID AND ProgrammeCourse.courseCode = Course.courseCode AND Programme.programmeID = %s UNION SELECT courseName FROM Course,Programme,ProgrammeCourse WHERE Programme.programmeID = ProgrammeCourse.programmeID AND ProgrammeCourse.courseCode = Course.courseCode AND Programme.programmeID = %s"
        cursor.execute(allCoursesSql,(progID,cProgID))
        allCourses = cursor.fetchall()

        progNameSql = "Select programmeName from Programme WHERE programmeID=%s"
        cursor.execute(progNameSql,(cProgID))
        cName = cursor.fetchall()
        coursesSql = "SELECT courseName FROM Course,Programme,ProgrammeCourse WHERE Programme.programmeID = ProgrammeCourse.programmeID  AND ProgrammeCourse.courseCode = Course.courseCode AND Programme.programmeID = %s"
        cursor.execute(coursesSql,progID)
        courses1 = cursor.fetchall()
        cursor.execute(coursesSql,(cProgID))
        courses2 = cursor.fetchall()
    cursor.close()
    return render_template("ProgCompare.html",progID=progID,mName = mProg,cName=cName,progList=progList, sDict = sortedDict,prog_data=prog_data,allCourses = allCourses,courses1 = courses1, courses2 = courses2)

@app.route("/admin/viewip", methods=['GET'])
def Admin_View_IP():
    return render_template('ViewIP.html')

@app.route("/admin/getip", methods=["POST"])
def Admin_Get_IP():
    try:
        db_conn2 = connections.Connection(
            host=customhost,
            port=3306,
            user=customuser,
            password=custompass,
            db=customdb,
            cursorclass=cursors.DictCursor,
        )
        cursor = db_conn2.cursor()
        if request.method == "POST":
            draw = request.form["draw"]
            row = int(request.form["start"])
            rowperpage = int(request.form["length"])
            searchValue = request.form["search[value]"]

            ## Total number of records without filtering
            cursor.execute("SELECT count(*) as allcount from LoginSession")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount["allcount"]
            searchValue = "%" + searchValue + "%"
            ## Total number of records with filtering
            cursor.execute("SELECT count(*) as allcount from LoginSession WHERE ipAddress LIKE %s",(searchValue))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount["allcount"]

            ## Fetch records
            if searchValue == "":
                cursor.execute("SELECT * FROM LoginSession ORDER BY loginTime limit %s, %s;",(row, rowperpage))
            else:
                cursor.execute(
                    "SELECT * FROM LoginSession WHERE ipAddress LIKE %s ORDER BY loginTime limit %s, %s;",(searchValue,row,rowperpage))
            offerlist = cursor.fetchall()
            data = []
            for row in offerlist:
                data.append(
                    {
                        "ip": row["ipAddress"],
                        "id": row["accountID"],                          
                        "loginTime": row["loginTime"],
                        "logoutTime": row["logoutTime"],                      
                    }
                )
            response = {
                "draw": draw,
                "iTotalRecords": totalRecords,
                "iTotalDisplayRecords": totalRecordwithFilter,
                "aaData": data,
            }
            return jsonify(response)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        db_conn2.close()

@app.route("/admin/userdetails/<id>", methods=["GET"])
def Admin_Get_User_Details(id):
    cursor = db_conn.cursor()    
    userSql = 'SELECT * FROM Account WHERE accountID=%s'
    cursor.execute(userSql,(id))
    user= cursor.fetchone()
    return render_template('UserDetails.html', user=user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)