from flask import Flask, render_template, request, redirect, url_for, send_file, session,  jsonify, json
from pymysql import connections, cursors
import os
from config import *
from io import BytesIO
from datetime import datetime
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

@app.route("/application")
def application():
    return render_template('Application.html')


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
    datetimeApplied = datetime.now()

    if(studHealth == 'Other'):
        studHealth = request.form["others"]

    fulladdress = studAddress + ", " + studPostcode + \
        ", " + studState + ", " + studCity
    cursor = db_conn.cursor()

    try:
        cursor.execute("INSERT INTO Applications VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       ("APP1", studName, studIc,
                        studGender, fulladdress, studEmail, datetimeApplied, "Pending", studPhone, guardianName, guardianNo,
                        studHealth, "ab", "v", "ProgC00001", "15"))
        db_conn.commit()

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    print("INSERT COMPLETE...")
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
    
    # Read image from which text needs to be extracted
    img = cv2.imread("static/media/test2.jpg")
    
    # Preprocessing the image starts
    
    # Convert the image to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Performing OTSU threshold
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    
    # Specify structure shape and kernel size.
    # Kernel size increases or decreases the area
    # of the rectangle to be detected.
    # A smaller value like (10, 10) will detect
    # each word instead of a sentence.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
    
    # Applying dilation on the threshold image
    dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
    
    # Finding contours
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
                                                    cv2.CHAIN_APPROX_NONE)
    
    # Creating a copy of image
    im2 = img.copy()
    
    # A text file is created and flushed
    file = open("recognized.txt", "w+")
    file.write("")
    file.close()
    
    # Looping through the identified contours
    # Then rectangular part is cropped and passed on
    # to pytesseract for extracting text from it
    # Extracted text is then written into the text file
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Drawing a rectangle on copied image
        rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Cropping the text block for giving input to OCR
        cropped = im2[y:y + h, x:x + w]
        
        # Open the file in append mode
        file = open("recognized.txt", "a")
        
        # Apply OCR on the cropped image
        text = pytesseract.image_to_string(cropped)
        
        # Appending the text into file
        file.write(text)
        file.write("\n")
        
        # Close the file
        file.close
        # cv2.imshow("Lena Soderberg”, img)
        cv2.waitKey(0)
    return "abc"




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
