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
import os
import boto3
from config import *
from io import BytesIO
import re
from flask_mail import Mail

app = Flask(__name__)
app.config["SECRET_KEY"] = "sem-sk"
region = customregion

db_conn = connections.Connection(
    host=customhost, port=3306, user=customuser, password=custompass, db=customdb
)
mail = Mail()

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("Login.html")

def checkEmail(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

def send_confirmation_email(user):
    confirmation_link = url_for('confirm_email', token=token, _external=True)

    msg = Message('Please confirm your email address', sender='noreply@example.com', recipients=[user.email])
    msg.body = 'Please click the following link to confirm your email address:\n\n{}'.format(confirmation_link)

    mail.send(msg)

@app.route("/account/login", methods=["GET", "POST"])
def login():
    return render_template("Login.html")


@app.route("/AJAXLogin", methods=["GET", "POST"])
def AJAXLogin():
    action = request.form.get("act")
    femail = request.form.get("femail")
    password = request.form.get("fpassword")

    cursor = db_conn.cursor(cursors.DictCursor)

    response = {}
    role = ""
    msg = ""
    msgdesc = ""

    if action == "login":
        login_sql = "SELECT * FROM Account WHERE accEmail=%s AND accPassword=%s;"
        try:
            cursor.execute(login_sql, (femail, password))
            user = cursor.fetchone()

            if user is not None:
                msg = "success"
                femail = user["accEmail"]

                if user['accStatus'] == 'verified':
                    msgdesc = ""
                    action = "login-success"

                    session['loggedin']=True
                    session['userid']=user['accountID']

                else:
                    msgdesc = "Invalid email or password"
                    action = "pending-verification"
            else:
                msg = "failed"
                action = "login-failed"
                if password == '':
                    msgdesc = "Please enter a password"
                else:
                    msgdesc = "Invalid email or password"
            
        except Exception as e:
            print(e)
            msg = 'failed'
            femail = user["accEmail"]
            action = "login-error"
            msgdesc=str(e)
        
        response = {
            "msg": msg,
            "femail": femail,
            "action": action,
            "msgdesc": msgdesc,
        }

    elif action == "create":
        register_sql = "INSERT INTO Account (accEmail, accPassword, accType, accStatus)VALUES (%s, %s, %s, %s)"
        check_exist_sql = "SELECT * FROM Account WHERE accEmail=%s"

        try:
            cursor.execute(check_exist_sql, femail)
            exist = cursor.fetchone()

            if exist is None:
                cursor.execute(register_sql, (femail, password, "user", "unverified"))
                db_conn.commit()
                msg = "success"
                response = {
                    "msg": msg,
                }
            else:
                msg = "failed"
                if not checkEmail(femail):
                    msgdesc = "Invalid email format"
                else:
                    msgdesc = "Email has already been used for registration."
                response = {"msg": msg, "msgdesc": msgdesc}

        except Exception as e:
            print(e)
            msg = "failed"
            msgdesc = str(e)
            response = {"msg": msg, "msgdesc": msgdesc}
    
    elif action == 'resend':
        try:
            
            if user is not None:
                msg = "success"
                femail = user["accEmail"]
                msgdesc = "The verification email has been sent to " + femail
            else:
                msg = "failed"
                femail = user["accEmail"]
                msgdesc = "Invalid email or password"
        except Exception as e:
            print(e)
            msg = 'failed'
            femail = user["accEmail"]
            msgdesc = str(e)

        response = {
            "msg": msg,
            "femail": femail,
            "action": action,
            "msgdesc": msgdesc,
        }

    return jsonify(response)


@app.route("/programme", methods=["GET", "POST"])
def Get_Programme():
    if request.method == "GET":
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
        return render_template("Programme.html", courses=data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
