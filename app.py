from flask import Flask, render_template, request, redirect, url_for, send_file, session,  jsonify, json
from pymysql import connections, cursors
import os
import boto3
from config import *
from io import BytesIO
from datetime import datetime
import numpy as np

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
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Programme ORDER BY ProgrammeID")
        progDetails = cursor.fetchall()
        cursor.execute("SELECT COUNT(Programme.programmeID) FROM Programme,ProgrammeCourse,Course WHERE Programme.programmeID = ProgrammeCourse.programmeID AND ProgrammeCourse.courseCode = Course.courseCode GROUP BY Programme.programmeID ORDER BY Programme.programmeID ")
        totalCourse = cursor.fetchall()
        cursor.execute("SELECT Course.CourseName FROM Course,ProgrammeCourse WHERE ProgrammeCourse.courseCode = Course.courseCode ORDER BY ProgrammeCourse.programmeID,Course.CourseName;")
        course = cursor.fetchall()
        return render_template('Programme.html',prog=progDetails,total=totalCourse,course=course)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
