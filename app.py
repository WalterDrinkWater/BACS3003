from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    session,
    jsonify,
    flash
)
from collections import defaultdict
from pymysql import connections, cursors
import os
from config import *
from io import BytesIO
import re
from flask_mail import Mail, Message
import datetime
import pytz

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
            "TAR UMT Online Application Login - Verify Your Email Address",
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
            "TAR UMT Online Application Login - Reset password",
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
                        session["useremail"] = user["accEmail"]
                        session["username"] = user["fullName"]
                        session_sql = "INSERT INTO LoginSession (ipAddress, loginTime, accountID)VALUES (%s, %s, %s)"
                        malaysia_timezone = pytz.timezone('Asia/Kuala_Lumpur')
                        malaysia_time = datetime.datetime.now().astimezone(malaysia_timezone)
                        cursor.execute(session_sql, (request.remote_addr, malaysia_time, user["accountID"]))
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


@app.route("/UpdateProfile", methods=["GET", "POST"])
def UpdateProfile():
    name = request.form.get("inputName")
    ic = request.form.get("inputIC")
    gender = request.form.get("inputGender")
    address = request.form.get("inputAddress")
    handphone = request.form.get("inputHandphoneNumber")
    email = request.form.get("inputEmail")

    try:
        cursor = db_conn.cursor(cursors.DictCursor)
        cursor.execute(
            "UPDATE Account SET fullName=%s, identification=%s, gender=%s, fullAddress=%s, handphoneNumber=%s WHERE accEmail=%s;",
            (name, ic, gender, address, handphone, email),
        )
        db_conn.commit()
        flash("Saved", category="success")
    except Exception as e:
        print(e)
    finally:
        cursor.close()

    return redirect(url_for("TempPage"))




@app.route("/programme", methods=["GET", "POST"])
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

        # Convert to a list if it is not already.
    #     if not isinstance(value, list):
    #         value = [value]

    #     data[key].extend(value)

    # cursor.close()
    # return render_template("Programme.html", courses=data)


@app.route("/admission/firstlogin", methods=["GET", "POST"])
def FirstLogin():
    return render_template("FirstLogin.html")


@app.route("/TempPage", methods=["GET", "POST"])
def TempPage():
    return render_template("TempPage.html")


# @app.route("/TempApp", methods=["GET", "POST"])
# def TempApp():
#     return render_template("TempApp.html")


# @app.route("/AJAXprogramme", methods=["GET", "POST"])
# def AJAXprogramme():
#     campus = request.form.get('campus')
#     programme = request.form.get('programme')
#     intake = request.form.get('intake')

#     select_sql = "SELECT c.campusID, c.campusName, p.programmeID, p.programmeName, i.intakeID, i.intakeName FROM ProgrammeCampus a, Programme p, Campus c, Intake i WHERE p.programmeID=a.programmeID AND c.campusID=a.campusID AND i.intakeID=a.intakeID"

#     parameters=[]
#     if campus is not None:
#         select_sql += " AND a.campusID=%s"
#         parameters.append(campus)

#     if programme is not None:
#         select_sql += " AND a.programmeID=%s"
#         parameters.append(programme)

#     if intake is not None:
#         select_sql += " AND a.intakeID=%s"
#         parameters.append(intake)

#     cursor = db_conn.cursor(cursors.DictCursor)
#     cursor.execute(select_sql, parameters)
#     records = cursor.fetchall()

#     campusID = set()
#     campusName = set()
#     programmeID = set()
#     programmeName = set()
#     intakeID = set()
#     intakeName = set()

#     for record in records:
#         campusID.add(record['campusID'])
#         campusName.add(record['campusName'])
#         programmeID.add(record['programmeID'])
#         programmeName.add(record['programmeName'])
#         intakeID.add(record['intakeID'])
#         intakeName.add(record['intakeName'])

#     response = {
#         "campusID":list(campusID),
#         "campusName":list(campusName),
#         "programmeID":list(programmeID),
#         "programmeName":list(programmeName),
#         "intakeID":list(intakeID),
#         "intakeName":list(intakeName),
#     }
#     return jsonify(response)


@app.route("/admission/addenquiry", methods=["GET", "POST"])
def AddEnquiry():
    id = session['userid']
    user_sql = "SELECT * FROM Account WHERE accountID=%s"
    try:
        cursor = db_conn.cursor(cursors.DictCursor)
        cursor.execute(user_sql, id)
        user = cursor.fetchone()
        return render_template("AddEnquiry.html", name=user['fullName'], phone=user['handphoneNumber'], email=user['accEmail'])
    except Exception as e:
        print(e)
    finally:
        cursor.close()


@app.route("/AddEnquiry", methods=["GET", "POST"])
def addEnquiry():
    id = session['userid']
    topic = request.form.get('inputTopic')
    title = request.form.get('inputTitle')
    question = request.form.get('inputQuestion')
    file = request.files['inputFile']
      
    try:
        malaysia_timezone = pytz.timezone('Asia/Kuala_Lumpur')
        malaysia_time = datetime.datetime.now().astimezone(malaysia_timezone)
        cursor = db_conn.cursor(cursors.DictCursor)
        cursor.execute("INSERT INTO Enquiry (enquiryTopic, enquiryTitle, question, datetimeEnquire, enquiryStatus, enquiryAccountID)VALUES (%s, %s, %s, %s, %s, %s)",(topic, title, question, malaysia_time, 'Pending Reply', id))
        db_conn.commit()
        enquiryID = cursor.lastrowid
        path = "static/media/" + str(enquiryID)  + "_" + file.filename
        file.save(os.path.join(path))
        cursor.execute("UPDATE Enquiry SET enquiryImagePath=%s WHERE enquiryID=%s",  (path, enquiryID))
        db_conn.commit()
        flash("Enquiry form has been submitted. Takes up to 3 working days to receive reply.", category='success')
    except Exception as e:
        print(e)
    finally:
        cursor.close()
    
    return redirect(url_for("AddEnquiry"))


@app.route("/admission/enquirydetails", methods=["GET", "POST"])
def enquiryDetails():
    enquiryID = request.args.get('id')
    enquiry_sql = "SELECT Enquiry.*, Account1.fullName AS enquiryAccountFullName, Account1.handphoneNumber AS enquiryAccountHandphoneNumber, Account1.accEmail AS enquiryAccountEmail, Account2.fullName AS responseAccountFullName, Account2.handphoneNumber AS responseAccountHandphoneNumber, Account2.accEmail AS responseAccountEmail FROM Enquiry LEFT JOIN Account AS Account1 ON Enquiry.enquiryAccountID = Account1.accountID LEFT JOIN Account AS Account2 ON Enquiry.responseAccountID = Account2.accountID WHERE enquiryID=%s;"
    try:
        cursor = db_conn.cursor(cursors.DictCursor)
        cursor.execute(enquiry_sql, enquiryID)
        enquiry = cursor.fetchone()

        return render_template("EnquiryDetails.html", enquiry=enquiry)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
    return render_template("EnquiryDetails.html", enquiry=enquiry)


@app.route("/admission/enquiry", methods=["GET", "POST"])
def enquiry():
    return render_template("EnquiryList.html")


@app.route("/AJAXenquirylist", methods=["GET", "POST"])
def AJAXenquirylist():
    enquiryID = session['userid']
    draw = request.form["draw"]
    row = int(request.form["start"])
    rowperpage = int(request.form["length"])
    searchValue = request.form["search[value]"]
    
    try:
        cursor = db_conn.cursor(cursors.DictCursor)

        ## Total number of records without filtering
        cursor.execute(
            "SELECT count(*) as allcount FROM Enquiry WHERE enquiryAccountID=%s", enquiryID
        )
        rsallcount = cursor.fetchone()
        totalRecords = rsallcount["allcount"]

        ## Total number of records with filtering
        likeString = "%" + searchValue + "%"
        cursor.execute(
            "SELECT count(*) as allcount FROM Enquiry WHERE (enquiryTopic LIKE %s OR enquiryTitle LIKE %s OR question LIKE %s OR enquiryStatus LIKE %s) AND enquiryAccountID=%s",
            (
                likeString,
                likeString,
                likeString,
                likeString,
                enquiryID,
            ),
        )
        rsallcount = cursor.fetchone()
        totalRecordwithFilter = rsallcount["allcount"]

        ## Fetch records
        if searchValue == "":
            cursor.execute(
                "SELECT * FROM Enquiry WHERE enquiryAccountID=%s ORDER BY CASE enquiryStatus WHEN 'Pending Reply' THEN 0 WHEN 'Completed' THEN 1 END ASC, datetimeEnquire DESC limit %s, %s;",
                (enquiryID, row, rowperpage),
            )
            records = cursor.fetchall()
        else:
            cursor.execute(
                "SELECT * FROM Enquiry WHERE (enquiryTopic LIKE %s OR enquiryTitle LIKE %s OR question LIKE %s OR enquiryStatus LIKE %s) AND enquiryAccountID=%s ORDER BY CASE enquiryStatus WHEN 'Pending Reply' THEN 0 WHEN 'Completed' THEN 1 END ASC, datetimeEnquire DESC limit %s, %s;",
                (
                    likeString,
                    likeString,
                    likeString,
                    likeString,
                    enquiryID,
                    row,
                    rowperpage,
                ),
            )
            records = cursor.fetchall()

        data = []
        for row in records:
            data.append(
                {
                    "enquiryID": row["enquiryID"],
                    "datetimeEnquire": row["datetimeEnquire"].strftime(
                        "%d-%m-%Y %I:%M:%S %p"
                    ),
                    "enquiryTopic": row["enquiryTopic"],
                    "enquiryTitle": row["enquiryTitle"],
                    "enquiryStatus": row["enquiryStatus"],
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


@app.route("/admin/enquiry", methods=["GET", "POST"])
def adminEnquiry():
    return render_template("AdminEnquiryList.html")


@app.route("/AddResponse", methods=["GET", "POST"])
def addResponse():

    adminid = session['userid']
    enquiryid = request.form.get('inputEnquiryID')
    feedback = request.form.get('inputQuestion')
    file = request.files['inputFile']
    
    try:
        malaysia_timezone = pytz.timezone('Asia/Kuala_Lumpur')
        malaysia_time = datetime.datetime.now().astimezone(malaysia_timezone)
        cursor = db_conn.cursor(cursors.DictCursor)
        cursor.execute("UPDATE Enquiry SET responseAccountID=%s, response=%s, datetimeResponse=%s, enquiryStatus=%s WHERE enquiryID=%s", (adminid, feedback, malaysia_time, 'Completed', enquiryid))
        db_conn.commit()
        if file.filename != '':
            path = "static/media/" + str(enquiryid)  + "_" + file.filename
            file.save(os.path.join(path))
            cursor.execute("UPDATE Enquiry SET responseImagePath=%s WHERE enquiryID=%s",  (path, enquiryid))
            db_conn.commit()
        flash("A response has been submitted.", category='success')
    except Exception as e:
        print(e)
    finally:
        cursor.close()
    
    return redirect(url_for("adminEnquiryDetails", id=enquiryid))


@app.route("/admin/enquirydetails", methods=["GET", "POST"])
def adminEnquiryDetails():
    enquiryID = request.args.get('id')
    enquiry_sql = "SELECT Enquiry.*, Account1.fullName AS enquiryAccountFullName, Account1.handphoneNumber AS enquiryAccountHandphoneNumber, Account1.accEmail AS enquiryAccountEmail, Account2.fullName AS responseAccountFullName, Account2.handphoneNumber AS responseAccountHandphoneNumber, Account2.accEmail AS responseAccountEmail FROM Enquiry LEFT JOIN Account AS Account1 ON Enquiry.enquiryAccountID = Account1.accountID LEFT JOIN Account AS Account2 ON Enquiry.responseAccountID = Account2.accountID WHERE enquiryID=%s;"
    try:
        cursor = db_conn.cursor(cursors.DictCursor)
        cursor.execute(enquiry_sql, enquiryID)
        enquiry = cursor.fetchone()

        return render_template("AdminEnquiryDetails.html", enquiry=enquiry)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
    return render_template("AdminEnquiryDetails.html", enquiry=enquiry)


@app.route("/AJAXadminenquirylist", methods=["GET", "POST"])
def AJAXadminenquirylist():
    draw = request.form["draw"]
    row = int(request.form["start"])
    rowperpage = int(request.form["length"])
    searchValue = request.form["search[value]"]
    
    try:
        cursor = db_conn.cursor(cursors.DictCursor)

        ## Total number of records without filtering
        cursor.execute(
            "SELECT count(*) as allcount FROM Enquiry"
        )
        rsallcount = cursor.fetchone()
        totalRecords = rsallcount["allcount"]

        ## Total number of records with filtering
        likeString = "%" + searchValue + "%"
        cursor.execute(
            "SELECT count(*) as allcount FROM Enquiry WHERE enquiryTopic LIKE %s OR enquiryTitle LIKE %s OR question LIKE %s OR enquiryStatus LIKE %s",
            (
                likeString,
                likeString,
                likeString,
                likeString,
            ),
        )
        rsallcount = cursor.fetchone()
        totalRecordwithFilter = rsallcount["allcount"]

        ## Fetch records
        if searchValue == "":
            cursor.execute(
                "SELECT * FROM Enquiry ORDER BY CASE enquiryStatus WHEN 'Pending Reply' THEN 0 WHEN 'Completed' THEN 1 END ASC, datetimeEnquire DESC limit %s, %s;",
                (row, rowperpage),
            )
            records = cursor.fetchall()
        else:
            cursor.execute(
                "SELECT * FROM Enquiry WHERE enquiryTopic LIKE %s OR enquiryTitle LIKE %s OR question LIKE %s OR enquiryStatus LIKE %s ORDER BY CASE enquiryStatus WHEN 'Pending Reply' THEN 0 WHEN 'Completed' THEN 1 END ASC, datetimeEnquire DESC limit %s, %s;",
                (
                    likeString,
                    likeString,
                    likeString,
                    likeString,
                    row,
                    rowperpage,
                ),
            )
            records = cursor.fetchall()

        data = []
        for row in records:
            data.append(
                {
                    "enquiryID": row["enquiryID"],
                    "datetimeEnquire": row["datetimeEnquire"].strftime(
                        "%d-%m-%Y %I:%M:%S %p"
                    ),
                    "enquiryTopic": row["enquiryTopic"],
                    "enquiryTitle": row["enquiryTitle"],
                    "enquiryStatus": row["enquiryStatus"],
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
    

@app.route("/logout", methods=["GET", "POST"])
def logout():
    id = session['userid']
    logout_sql = "UPDATE LoginSession SET logoutTime=%s WHERE accountID=%s"
    try:
        cursor = db_conn.cursor(cursors.DictCursor)
        malaysia_timezone = pytz.timezone('Asia/Kuala_Lumpur')
        malaysia_time = datetime.datetime.now().astimezone(malaysia_timezone)
        cursor.execute(logout_sql, (malaysia_time,id))
        db_conn.commit()
        session['loggedin'] = False
        session.pop('userid', None)
        session.pop('username', None)

        return redirect(url_for("home"))
    except Exception as e:
        print(e)
    finally:
        cursor.close()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
