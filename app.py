from flask import Flask, render_template, request, redirect, url_for, send_file, session,  jsonify, json
from pymysql import connections, cursors
import os
import boto3
from config import *
from io import BytesIO

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
    return render_template('Login.html')

@app.route("/programme", methods=['GET', 'POST'])
def Get_Programme():
    if request.method == 'GET':
        cursor = db_conn.cursor(cursors.DictCursor)
        query = "SELECT programmeName, courseName FROM Programme p, ProgrammeCourse d, Course c WHERE p.programmeID=d.programmeID AND d.courseCode=c.courseCode ORDER BY p.programmeID ASC, c.courseCode ASC"
        cursor.execute(query)
        courses = cursor.fetchall()

        data = {}
        for row in courses:
            key = row["programmeName"]
            if key not in data:
                data[key] = []
            value = row["courseName"]

            # Convert to a list if it is not already.
            if not isinstance(value, list):
                value = [value]

            data[key].extend(value)
            
        cursor.close()
        return render_template('Programme.html', courses=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)