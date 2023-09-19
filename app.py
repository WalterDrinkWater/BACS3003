from flask import Flask, render_template, request, redirect, url_for, send_file, session,  jsonify, json
from pymysql import connections, cursors
import os
import boto3
from config import *
from io import BytesIO
from datetime import datetime
import numpy as np
import cv2
import pytesseract
from collections import defaultdict

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

@app.route("/application/apply", methods=['POST'])
def apply():
    studName = request.form["name"]
    studIc = request.form["ic"]
    studGender = request.form["gender"]
    studAddress = request.form["address"]
    studPostcode = request.form["postcode"]
    studState = request.form["state"]
    studCity = request.form["city"]
    studPhone = request.form["phone"]
    guardianName = request.form["guardName"]
    guardianNo = request.form["guardNo"]
    studEmail = request.form["email"]
    studHealth = request.form["selectHealth"]
    datetimeApplied = datetime.Now()

    if(studHealth == 'Other'):
        studHealth = request.form["others"]

    fulladdress = studAddress + ", " + studPostcode + \
        ", " + studState + ", " + studCity
    cursor = db_conn.cursor()

    try:
        cursor.execute("INSERT INTO Applications VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       ("APP", studName, studIc,
                        studGender, fulladdress, studEmail, datetimeApplied, studPhone, guardianName, guardianNo,
                        studHealth, "PROGRAMME", "ACC"))
        db_conn.commit()

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template("AddEmpOutput.html")

@app.route("/programme", methods=['GET', 'POST'])
def Get_Programme():
    if request.method == 'GET':
        # cursor = db_conn.cursor(cursors.DictCursor)
        # query = "SELECT programmeName, courseName FROM Programme p, ProgrammeCourse d, Course c WHERE p.programmeID=d.programmeID AND d.courseCode=c.courseCode ORDER BY p.programmeID ASC, c.courseCode ASC"
        # cursor.execute(query)
        # courses = cursor.fetchall()

        # data = {}
        # for row in courses:
        #     key = row["programmeName"]
        #     if key not in data:
        #         data[key] = []
        #     value = row["courseName"]

        #     # Convert to a list if it is not already.
        #     if not isinstance(value, list):
        #         value = [value]

        #     data[key].extend(value)

        cursor = db_conn.cursor()
        query = "SELECT * FROM Programme"
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

        for row in tempReq:
            group_key = row[3]
            grouped_data[group_key].append(row)
        
        return render_template('ProgDetails.html', prog=prog ,course=course, req=grouped_data)
    
# 



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
