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
        progOvSql = "SELECT intakeYear,intakeMonth,programmeDuration,campusName FROM Programme,ProgrammeCampus,Intake,Campus WHERE Programme.programmeID = ProgrammeCampus.programmeID  AND Intake.IntakeID = ProgrammeCampus.intakeID AND Campus.campusID = ProgrammeCampus.campusID AND Programme.programmeID = %s"
        cursor.execute(progOvSql,(progID))        
        ov = cursor.fetchall()
        for row in tempReq:
            group_key = row[3]
            grouped_data[group_key].append(row)
        cursor.close()
        return render_template('ProgDetails.html', prog=prog ,course=course, req=grouped_data,ov=ov)

@app.route("/progCompare/<progID>", methods=['GET', 'POST'])
def Compare_Programme(progID):
    cursor = db_conn.cursor()    
    if request.method == 'GET':
        mainProg = "Select programmeName from Programme WHERE programmeID = %s"
        cursor.execute(mainProg,(progID))
        mProg = cursor.fetchall()
        progListSql = "Select programmeName,programmeID from Programme WHERE programmeID != %s"
        cursor.execute(progListSql,(progID))
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
        for prog_name, alevel_sub, alevel_grade, diploma_grade in allReq:
            prog_data.append({
            "Program": prog_name,
            "Subject": alevel_sub,
            "Grade": alevel_grade
            })
        print(allReq)
    cursor.close()
    return render_template("ProgCompare.html",mName = mProg,progList=progList, sDict = sortedDict,prog_data=prog_data)

@app.route("/about", methods=['GET', 'POST'])
def About_Us():

    try:
        cursor = db_conn.cursor(cursors.DictCursor)
        cursor.execute("SELECT campusName, campusLocation, campusURL FROM Campus")
        campuses = cursor.fetchall()
        cursor.execute("SELECT academicianID, academicianName, academicianTitle, academicianEmail, designation, department, educationBackground, publication, researchArea, organizationMembership, academicianURL FROM Academician")
        academicians = cursor.fetchall()

    except Exception as e:
            return str(e)
    
    return render_template('About.html', campuses=campuses, academicians=academicians)

@app.route("/academicianDetails", methods=['GET','POST'])
def View_Aca_Details():
    if request.method == "GET":
        selectedAcaID = request.args.get("selectedAca")

    try:
        cursor = db_conn.cursor(cursors.DictCursor)
        cursor.execute("SELECT academicianID, academicianName, academicianTitle, academicianEmail, designation, department, educationBackground, publication, researchArea, organizationMembership, academicianURL FROM Academician WHERE academicianID = %s", (selectedAcaID))
        acaDetails = cursor.fetchone()

    except Exception as e: 
            return str(e)

    finally:
        cursor.close()

    return render_template('AcademicianDetails.html', acaDetails=acaDetails)

# @app.route("/test")
# def scan_img():
#     # Mention the installed location of Tesseract-OCR in your system
#     pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'
    
#     # Read image from which text needs to be extracted
#     img = cv2.imread("static/media/test2.jpg")
    
#     # Preprocessing the image starts
    
#     # Convert the image to gray scale
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
#     # Performing OTSU threshold
#     ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    
#     # Specify structure shape and kernel size.
#     # Kernel size increases or decreases the area
#     # of the rectangle to be detected.
#     # A smaller value like (10, 10) will detect
#     # each word instead of a sentence.
#     rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
    
#     # Applying dilation on the threshold image
#     dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
    
#     # Finding contours
#     contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
#                                                     cv2.CHAIN_APPROX_NONE)
    
#     # Creating a copy of image
#     im2 = img.copy()
    
#     # A text file is created and flushed
#     file = open("recognized.txt", "w+")
#     file.write("")
#     file.close()
    
#     # Looping through the identified contours
#     # Then rectangular part is cropped and passed on
#     # to pytesseract for extracting text from it
#     # Extracted text is then written into the text file
#     for cnt in contours:
#         x, y, w, h = cv2.boundingRect(cnt)
        
#         # Drawing a rectangle on copied image
#         rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
#         # Cropping the text block for giving input to OCR
#         cropped = im2[y:y + h, x:x + w]
        
#         # Open the file in append mode
#         file = open("recognized.txt", "a")
        
#         # Apply OCR on the cropped image
#         text = pytesseract.image_to_string(cropped)
        
#         # Appending the text into file
#         file.write(text)
#         file.write("\n")
        
#         # Close the file
#         file.close
#         cv2.imshow("Lena Soderberg”, img)
#         cv2.waitKey(0)
#     return "abc"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)