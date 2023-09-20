from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    session,
    jsonify,
    json,
)
from pymysql import connections, cursors
import pymysql
import os
from config import *
from io import BytesIO
from datetime import datetime
import re
# from flask_mail import Mail, Message
import datetime
# import pytz
import cv2
import pytesseract
from collections import defaultdict

app = Flask(__name__)
app.config["SECRET_KEY"] = "sem-sk"
region = customregion
app.config["MAIL_SERVER"] = "smtp-relay.brevo.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "hokw-wm20@student.tarc.edu.my"
app.config["MAIL_PASSWORD"] = "XB1MN3PVgzbOhmGy"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
mail = Mail(app)


db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb,
    connect_timeout=86400,
)
output = {}

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template('Index.html')

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