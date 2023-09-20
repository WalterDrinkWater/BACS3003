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
from flask_mail import Mail, Message
from datetime import datetime

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


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("Index.html")


@app.route("/index", methods=["GET", "POST"])
def index():
    return render_template("Index.html")


def checkEmail(email):
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    if re.fullmatch(regex, email):
        return True
    else:
        return False


@app.route("/confirm-email/<email>", methods=["GET", "POST"])
def confirm_email(email):
    cursor = db_conn.cursor(cursors.DictCursor)
    login_sql = "SELECT * FROM Account WHERE accEmail=%s;"
    cursor.execute(login_sql, email)
    user = cursor.fetchone()

    msg = ""
    result = ""
    if user is None:
        msg = "Email not found"
        result = "failed"
    elif user["accStatus"] == "verified":
        msg = "Email has already verified"
        result = "failed"
    else:
        cursor.execute(
            "UPDATE Account SET accStatus = %s WHERE accountID=%s;",
            ("verified", user["accountID"]),
        )
        db_conn.commit()
        msg = "Your email has been verified"
        result = "success"
    cursor.close()
    return render_template(
        "EmailVerification.html", email=email, msg=msg, result=result
    )


def send_confirmation_email(email):
    select_sql = "SELECT * FROM Account WHERE accEmail=%s"
    cursor = db_conn.cursor(cursors.DictCursor)
    cursor.execute(select_sql, email)
    user = cursor.fetchone()
    cursor.close()
    if user is not None:
        confirmation_link = url_for("confirm_email", email=email, _external=True)
        msg = Message(
            "TAR UMT Online Application Login",
            sender="noreply@example.com",
            recipients=[email],
        )
        msg.body = "Please click the following link to confirm your email address:\n\n{}".format(
            confirmation_link
        )
        mail.send(msg)
    

def send_reset_email(email):
    select_sql = "SELECT * FROM Account WHERE accEmail=%s"
    cursor = db_conn.cursor(cursors.DictCursor)
    cursor.execute(select_sql, email)
    user = cursor.fetchone()
    cursor.close()
    if user is not None:
        confirmation_link = url_for("ResetPassword", email=email, _external=True)
        msg = Message(
            "TAR UMT Reset Password",
            sender="noreply@example.com",
            recipients=[email],
        )
        msg.body = "You recently requested a password reset to your TAR UMT account.\n\nPlease click the following link to reset your password:\n\n{}".format(
            confirmation_link
        )
        mail.send(msg)

@app.route("/account/login", methods=["GET", "POST"])
def login():
    return render_template("Login.html")


@app.route("/AJAXLogin", methods=["GET", "POST"])
def AJAXLogin():
    response = {}
    if request.method == 'POST':
        action = request.form.get("act")
        femail = request.form.get("femail")
        password = request.form.get("fpassword")

        cursor = db_conn.cursor(cursors.DictCursor)

        msg = ""
        msgdesc = ""
        nexturl = ""
        if action == "login":
            login_sql = "SELECT * FROM Account WHERE accEmail=%s AND accPassword=%s;"
            try:
                cursor.execute(login_sql, (femail, password))
                user = cursor.fetchone()
                if user is not None:
                    msg = "success"
                    femail = user["accEmail"]

                    if user["accStatus"] == "verified":
                        msgdesc = ""
                        action = "login-success"
                        if user["accType"] == 'user':
                            nexturl = "/index"
                        elif user["accType"] == 'admin':
                            nexturl = "/programme"
                            
                        session["loggedin"] = True
                        session["userid"] = user["accountID"]
                        session["username"] = user["fullName"]
                        session_sql = "INSERT INTO LoginSession (ipAddress, loginTime, accountID)VALUES (%s, %s, %s)"
                        print(datetime.now(datetime.timezone.utc).astimezone().tzname())
                        cursor.execute(session_sql, (request.remote_addr, datetime.now(), user["accountID"]))
                        db_conn.commit()
                    else:
                        msgdesc = "Invalid email or password"
                        action = "pending-verification"
                else:
                    msg = "failed"
                    action = "login-failed"
                    if password == "":
                        msgdesc = "Please enter a password"
                    else:
                        msgdesc = "Invalid email or password"

            except Exception as e:
                print(e)
                msg = "failed"
                femail = user["accEmail"]
                action = "login-error"
                msgdesc = str(e)
            finally:
                cursor.close()

            response = {
                "msg": msg,
                "femail": femail,
                "action": action,
                "msgdesc": msgdesc,
                "nexturl": nexturl,
            }

        elif action == "create":
            register_sql = "INSERT INTO Account (accEmail, accPassword, accType, accStatus)VALUES (%s, %s, %s, %s)"
            check_exist_sql = "SELECT * FROM Account WHERE accEmail=%s"

            try:
                if not checkEmail(femail):
                    msg="failed"
                    msgdesc = "Invalid email format"
                    response = {"msg": msg, "msgdesc": msgdesc}
                else:
                    cursor.execute(check_exist_sql, femail)
                    exist = cursor.fetchone()
                    cursor.close()

                    if exist is None:
                        cursor = db_conn.cursor(cursors.DictCursor)
                        cursor.execute(register_sql, (femail, password, "user", "unverified"))
                        db_conn.commit()
                        cursor.close()
                        
                        msg = "success"
                        send_confirmation_email(femail)
                        response = {
                            "msg": msg,
                        }
                    else:
                        msg = "failed"
                        msgdesc = "Email has already been used for registration."
                        response = {"msg": msg, "msgdesc": msgdesc}

            except Exception as e:
                print(e)
                msg = "failed"
                msgdesc = str(e)
                response = {"msg": msg, "msgdesc": msgdesc}

        elif action == "resend":
            try:
                resend_sql = "SELECT * FROM Account WHERE accEmail=%s"
                cursor.execute(resend_sql, (femail))
                user = cursor.fetchone()
                cursor.close()
                
                if user is not None:
                    msg = "success"
                    femail = user["accEmail"]
                    send_confirmation_email(femail)
                    msgdesc = "The verification email has been sent to " + femail

            except Exception as e:
                print(e)
                msg = "failed"
                femail = user["accEmail"]
                msgdesc = str(e)
            finally:
                cursor.close()

            response = {
                "msg": msg,
                "femail": femail,
                "action": action,
                "msgdesc": msgdesc,
            }

        elif action == "request-reset":
            
            if not checkEmail(femail):
                msg = "failed"
                msgdesc = "Invalid email format"
            else:
                msg = "success"
                send_reset_email(femail)
                msgdesc = "If we have an account for the email address you provided, we have emailed the instruction to reset your password. (The email might take a few minutes to arrive)"
                
            response = {
                "msg": msg,
                "msgdesc": msgdesc,
            }
    return jsonify(response)


@app.route("/account/verification", methods=["GET", "POST"])
def Verification():
    if request.method == "POST":
        verify_email = request.form.get("verify_email")
        return render_template("Verification.html", verify_email=verify_email)


@app.route("/account/resetpassword", methods=["GET", "POST"])
def ResetPassword():
    return render_template("ResetPassword.html", email=request.args.get("email"))


@app.route("/AJAXResetPassword", methods=["GET", "POST"])
def AJAXResetPassword():
    email = request.form.get("femail")
    password = request.form.get("fpassword")

    msg = ""
    msgdesc = ""
    try:
        cursor = db_conn.cursor(cursors.DictCursor)
        cursor.execute(
            "UPDATE Account SET accPassword=%s WHERE accEmail=%s;",
            (password, email),
        )
        db_conn.commit()
        msg = "success"
        msgdesc = "Password has been reset succesfully"
    except Exception as e:
        print(e)
        msg = "failed"
        msgdesc = str(e)

    cursor.close()
    response = {
        "msg": msg,
        "msgdesc": msgdesc
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
