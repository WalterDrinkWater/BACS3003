from flask import Flask, render_template, request, redirect, url_for, send_file, session,  jsonify, json
from pymysql import connections, cursors
import os
from config import *
from io import BytesIO
from datetime import datetime
import numpy as np
import cv2
import pytesseract
from imutils.perspective import four_point_transform
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

@app.route("/studhome")
def studhome():
    try:
        cursor = db_conn.cursor(cursors.DictCursor)
        cursor.execute("SELECT * FROM Applications WHERE accountID=%s", ("1"))
        application = cursor.fetchall()

    except Exception as e:
        return str(e)

    finally:
        cursor.close()
    
    return render_template('StudHome.html', application=application)

@app.route("/application")
def application():
    id = request.args.get("id")
    if(id != None):
        try:
            cursor = db_conn.cursor(cursors.DictCursor)
            cursor.execute("SELECT * FROM Applications WHERE applicationID=%s", (id))
            application = cursor.fetchone()

        except Exception as e:
            return str(e)

        finally:
            cursor.close()
    else:
        application = ""
    
    return render_template('Application.html', application=application)

@app.route("/application/apply/<status>", methods=['POST'])
def apply(status):
    if(status == 'insertinfo'):
        cursor = db_conn.cursor()

        studName = request.form["name"]
        studIc = request.form["ic"]
        studGender = request.form["gender"]
        studAddress = request.form["address"]
        studPhone = request.form["phone"]
        guardianName = request.form["guardName"]
        guardianNo = request.form["guardNo"]
        studEmail = request.form["email"]
        studHealth = request.form["selectHealth"]
        datetimeApplied = datetime.now()
        # accId = session["userid"]

        if(studHealth == 'Other'):
            studHealth = request.form["others"]

        cursor = db_conn.cursor()

        try:
            cursor.execute("INSERT INTO Applications VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        ("APP3", studName, studIc,
                            studGender, studAddress, studEmail, datetimeApplied, "Pending", studPhone, guardianName, guardianNo,
                            studHealth, "", "", "ProgC00001", "1"))
            db_conn.commit()

        except Exception as e:
            return str(e)

        finally:
            cursor.close()
    else: 
        studName = request.form["name"]
        studIc = request.form["ic"]
        studGender = request.form["gender"]
        studAddress = request.form["address"]
        studPhone = request.form["phone"]
        guardianName = request.form["guardName"]
        guardianNo = request.form["guardNo"]
        studEmail = request.form["email"]
        studHealth = request.form["selectHealth"]
        datetimeApplied = datetime.now()

        if(studHealth == 'Other'):
            studHealth = request.form["others"]

        cursor = db_conn.cursor()

        try:
            cursor.execute("UPDATE applications SET studentName = %s, identification = %s, gender = %s, fullAddress = %s,"
                           + "email = %s, datetimeApplied = %s, handphoneNumber = %s, guardianName = %s," +
                            "guardianNumber = %s, healthIssue = %s, programmeCampusID = %s)",
                        (studName, studIc, studGender, studAddress, studEmail, datetimeApplied, studPhone, guardianName, 
                         guardianNo,studHealth, "ProgC00001"))
            db_conn.commit()

        except Exception as e:
            return str(e)

        finally:
            cursor.close()

    print("INSERT COMPLETE...")
    return redirect(url_for('application', id="APP3"))

@app.route('/application/uploadic', methods=['POST'])
def uploadic():
    id = request.args.get("id")
    icf = request.files["frontIc"]
    icb = request.files["backIc"]

    cursor = db_conn.cursor()

    try:
        if(icf != None):
            path = os.path.join("static/media/" + id + "_front_" + icf.filename)
            icf.save(path)
            cursor.execute("UPDATE Applications SET identificationFrontPath = %s WHERE applicationID=%s",(path, id))

        if(icf != None):
            path = os.path.join("static/media/" + id + "_back" + icb.filename)
            icf.save(path)
            cursor.execute("UPDATE Applications SET identificationBackPath = %s WHERE applicationID=%s",(path, id))

        db_conn.commit()

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return redirect(url_for('application'))


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
        cursor.execute(progSql, (progID))
        prog = cursor.fetchall()
        courseSql = "SELECT Course.* FROM Course,ProgrammeCourse,Programme WHERE Programme.programmeID = ProgrammeCourse.programmeID AND ProgrammeCourse.courseCode = Course.courseCode AND Programme.programmeID=%s ORDER BY CourseName"
        cursor.execute(courseSql, (progID))
        course = cursor.fetchall()
        reqSql = "SELECT * FROM QualificationSubject WHERE programmeID=%s ORDER BY qualificationName"
        cursor.execute(reqSql, (progID))
        tempReq = cursor.fetchall()
        grouped_data = defaultdict(list)

        for row in tempReq:
            group_key = row[3]
            grouped_data[group_key].append(row)

        return render_template('ProgDetails.html', prog=prog, course=course, req=grouped_data)

@app.route("/test")
def scan_img():
    # Mention the installed location of Tesseract-OCR in your system
    pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'
    
    # Load image, grayscale, Otsu's threshold
    image = cv2.imread('static/media/SPM Result.jpg')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Morph open to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    # Find contours and remove small noise
    cnts = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        area = cv2.contourArea(c)
        if area < 50:
            cv2.drawContours(opening, [c], -1, 0, -1)

    # Invert and apply slight Gaussian blur
    result = 255 - opening
    result = cv2.GaussianBlur(result, (3,3), 0)

    # Perform OCR
    data = pytesseract.image_to_string(result, lang='eng', config='--psm 6')
    print(data)

    cv2.namedWindow("thresh", cv2.WINDOW_NORMAL)
    cv2.namedWindow("opening", cv2.WINDOW_NORMAL)
    cv2.namedWindow("result", cv2.WINDOW_NORMAL)
    cv2.imshow('thresh', thresh)
    cv2.imshow('opening', opening)
    cv2.imshow('result', result)
    cv2.waitKey()     

    return data




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
