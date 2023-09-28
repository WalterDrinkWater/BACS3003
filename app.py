from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    session,
    jsonify,
    flash,
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
import cv2
import numpy as np
import pytesseract
import difflib

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
    connect_timeout=600,
    db=customdb
)
output = {}

@app.route("/studhome")
def studhome():
    accid = session["userid"]
    try:
        cursor = db_conn.cursor(cursors.DictCursor)
        cursor.execute("SELECT a.applicationID, intakeName, ap.programmeCampusID, p.programmeName, apStatus, applicationStatus FROM Applications a " +
                        "LEFT JOIN ApplicationProgramme ap ON a.applicationID = ap.applicationID " +
                        "LEFT JOIN ProgrammeCampus pc ON  ap.programmeCampusID = pc.programmeCampusID " +
                        "LEFT JOIN Programme p ON p.programmeID = pc.programmeID " +
                        "LEFT JOIN Intake i ON i.intakeID = pc.intakeID " +
                        " WHERE accountID = %s", (str(accid)))
        application = cursor.fetchall()
        # cursor.execute("SELECT * FROM Applications a, ApplicationProgramme ap, Programme p WHERE " +
        #                "a.applicationID = ap.applicationID AND ap.programmeID = p.programmeID AND accountID = %s", 
        #                (str(accid)))
        # choices = cursor.fetchall()

    except Exception as e:
        return str(e)

    finally:
        cursor.close()
    return render_template("StudHome.html", application=application)


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
    if request.method == "POST":
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
                        if user["accType"] == "user":
                            if (
                                user["fullName"] is None
                                or user["identification"] is None
                                or user["handphoneNumber"] is None
                            ):
                                nexturl = "/admission/firstlogin"
                            else:
                                nexturl = "/studhome"
                        elif user["accType"] == "admin":
                            nexturl = "/admin/viewip"

                        session["loggedin"] = True
                        session["userid"] = user["accountID"]
                        session["useremail"] = user["accEmail"]
                        session["username"] = user["fullName"]
                        session_sql = "INSERT INTO LoginSession (ipAddress, loginTime, accountID)VALUES (%s, %s, %s)"
                        malaysia_timezone = pytz.timezone("Asia/Kuala_Lumpur")
                        malaysia_time = datetime.datetime.now().astimezone(
                            malaysia_timezone
                        )
                        cursor.execute(
                            session_sql,
                            (request.remote_addr, malaysia_time, user["accountID"]),
                        )
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
                    msg = "failed"
                    msgdesc = "Invalid email format"
                    response = {"msg": msg, "msgdesc": msgdesc}
                else:
                    cursor.execute(check_exist_sql, femail)
                    exist = cursor.fetchone()
                    cursor.close()

                    if exist is None:
                        cursor = db_conn.cursor(cursors.DictCursor)
                        cursor.execute(
                            register_sql, (femail, password, "user", "unverified")
                        )
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
    response = {"msg": msg, "msgdesc": msgdesc}
    return jsonify(response)

@app.route("/application/personalinfo")
def application():
    if session["appid"] != None:
        appid = session["appid"]
        
    if(appid != None):
        try:
            cursor = db_conn.cursor(cursors.DictCursor)
            cursor.execute("SELECT * FROM Applications WHERE applicationID=%s", (appid))
            application = cursor.fetchone()

        except Exception as e:
            return str(e)

        finally:
            cursor.close()
    else:
        application = ""
    
    return render_template('PersonalInfo.html', application=application)

@app.route("/application/updateinfo", methods=['POST'])
def updateinfo():
    studName = request.form["name"]
    studIc = request.form["ic"]
    studGender = request.form["gender"]
    studAddress = request.form["address"]
    studPhone = request.form["phone"]
    guardianName = request.form["guardName"]
    guardianNo = request.form["guardNo"]
    studEmail = request.form["email"]
    studHealth = request.form["selectHealth"]
    datetimeApplied = datetime.datetime.now()
    appid = session["appid"]

    if(studHealth == 'Others'):
        studHealth = request.form["others"]

    cursor = db_conn.cursor()

    try:
        cursor.execute("UPDATE Applications SET studentName = %s, identification = %s, gender = %s, fullAddress = %s,"
                        + "email = %s, datetimeApplied = %s, handphoneNumber = %s, guardianName = %s," +
                        "guardianNumber = %s, healthIssue = %s WHERE applicationID = %s",
                    (studName, studIc, studGender, studAddress, studEmail, datetimeApplied, studPhone, guardianName, 
                        guardianNo,studHealth, appid))
        db_conn.commit()

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return redirect(url_for('application', id=appid))

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
            session["icf"] = "pass"

        if(icf != None):
            path = os.path.join("static/media/" + id + "_back_" + icb.filename)
            icf.save(path)
            cursor.execute("UPDATE Applications SET identificationBackPath = %s WHERE applicationID=%s",(path, id))
            session["icb"] = "pass"

        db_conn.commit()
        
    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return redirect(url_for('application'))

@app.route("/application/intake", methods=['GET', 'POST'])
def intake():
    if request.method == 'GET':
        if request.args.get("status") == 'edit':
            if request.args.get("id") != None:
                appid = request.args.get("id")
                session["appid"] = appid
            else:
                appid = session["appid"]
        
            try:
                cursor = db_conn.cursor(cursors.DictCursor)
                cursor.execute("SELECT i.intakeID,intakeName,c.campusID,campusName,p.programmeID, programmeType, programmeName FROM Applications a LEFT JOIN ApplicationProgramme ap ON a.applicationID = ap.applicationID LEFT JOIN ProgrammeCampus pc ON pc.programmeCampusID = ap.programmeCampusID LEFT JOIN Intake i ON pc.intakeID = i.intakeID LEFT JOIN Programme p ON pc.programmeID = p.programmeID LEFT JOIN Campus c ON pc.campusID = c.campusID WHERE a.applicationID=%s", (appid))
                application = cursor.fetchall()

            except Exception as e:
                return str(e)

            finally:
                cursor.close()
        else:
            if request.args.get("status") == 'insert':
                try:
                    cursor = db_conn.cursor(cursors.DictCursor)
                    accid = session["userid"]
                    cursor.execute("SELECT * FROM Account WHERE accountID = %s", (accid))
                    accinfo = cursor.fetchone()
                    datetimeApplied = datetime.datetime.now()

                    cursor.execute("INSERT INTO Applications (studentName, identification, gender, fullAddress, email, datetimeApplied, applicationStatus, handphoneNumber, accountID)"
                                + "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (accinfo["fullName"], accinfo["identification"],
                                accinfo["gender"], accinfo["fullAddress"], accinfo["accEmail"], datetimeApplied, "Pending", accinfo["handphoneNumber"], str(accid)))
                    db_conn.commit()
                    cursor.execute("SELECT * FROM Applications ORDER BY applicationID DESC LIMIT 1")
                    application = cursor.fetchone()
                    session["appid"] = application["applicationID"]
                    for _ in range (3):
                        cursor.execute("INSERT INTO ApplicationProgramme (applicationID) VALUES (%s)", (application["applicationID"]))
                        db_conn.commit()
                    session["intake"] = "fail"
                    session["icf"] = "fail"
                    session["icb"] = "fail"
                except Exception as e:
                    return str(e)

                finally:
                    cursor.close()
            else:
                application = ''
    campus_data = dynamic_selection()

    return render_template("Intake.html", campusdata=campus_data, application=application)

@app.route("/application/applyintake", methods=['GET', 'POST'])
def apply_intake():
    try:
        cursor = db_conn.cursor()
        intake = request.form["intake"]
        campus = request.form["campus"]
        prog = request.form["programme"]
        campus2 = request.form["campus2"]
        prog2 = request.form["programme2"]
        campus3 = request.form["campus3"]
        prog3 = request.form["programme3"]
        appid = session["appid"]

        cursor.execute("SELECT programmeCampusID, campusName, programmeID FROM ProgrammeCampus pc, Intake i, Campus c " +
                        "WHERE pc.intakeID = i.intakeID AND pc.campusID = c.campusID AND i.intakeName = %s " +
                        "AND programmeID = %s AND campusName = %s UNION ALL " +
                        "SELECT programmeCampusID, campusName, programmeID FROM ProgrammeCampus pc, Intake i, Campus c " +
                        "WHERE pc.intakeID = i.intakeID AND pc.campusID = c.campusID AND i.intakeName = %s " +
                        "AND programmeID = %s AND campusName = %s UNION ALL " +
                        "SELECT programmeCampusID, campusName, programmeID FROM ProgrammeCampus pc, Intake i, Campus c " +
                        "WHERE pc.intakeID = i.intakeID AND pc.campusID = c.campusID AND i.intakeName = %s " +
                        "AND programmeID = %s AND campusName = %s", (intake, prog, campus, intake, prog2, campus2 ,intake, prog3, campus3))
        progCampusIDs = cursor.fetchall()
        cursor.execute("SELECT apID FROM ApplicationProgramme WHERE applicationID = %s", (appid))
        apIDs = cursor.fetchall()
        for  pci, api in zip(progCampusIDs, apIDs):
            cursor.execute("UPDATE ApplicationProgramme SET applicationID = %s, programmeCampusID = %s WHERE apID = %s",
                        (appid, pci[0], api))
            db_conn.commit()
        session["intake"] = "pass"

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return redirect(url_for("intake", id=appid , status="edit"))

def dynamic_selection():
    try:
        cursor = db_conn.cursor(cursors.DictCursor)
        cursor.execute("SELECT DISTINCT i.intakeID, intakeName, campusID, pc.intakeID FROM Intake i, ProgrammeCampus pc WHERE i.intakeID = pc.intakeID")
        intakes = cursor.fetchall()
        cursor.execute("SELECT campusID, campusName FROM Campus")
        campuses = cursor.fetchall()
        cursor.execute("SELECT DISTINCT programmeType FROM Programme")
        progTypes = cursor.fetchall()
        cursor.execute("SELECT pc.programmeID, campusID, programmeName, programmeType FROM ProgrammeCampus pc, Programme p WHERE pc.programmeID = p.programmeID")
        progCampus = cursor.fetchall()
        campus_data = {}
        
        for intake in intakes:
            intakeName = intake["intakeName"]
            if intakeName in campus_data:
                pass
            else:
                campus_data[intakeName] = {}
            for campus in campuses:
                if campus["campusID"] == intake["campusID"]:
                    campus_name = campus["campusName"]
                    campus_id = campus["campusID"]
                    campus_data[intakeName][campus_name] = {}
                    for progType in progTypes:
                        if(progType["programmeType"] == "xDegree"):
                            campus_data[intakeName][campus_name]["Diploma"] = {}
                            campus_data[intakeName][campus_name]["Foundation"] = {}
                        else:
                            campus_data[intakeName][campus_name][progType["programmeType"]] = {}

                        for prog in progCampus:
                            if prog["campusID"] == campus_id and prog["programmeType"] == "Degree" and progType["programmeType"] == "Degree":
                                campus_data[intakeName][campus_name][progType["programmeType"]][prog["programmeID"]] = prog["programmeName"]
                            else: 
                                if("Diploma" in campus_data[intakeName][campus_name] and "Foundation" in campus_data[intakeName][campus_name]):
                                    if prog["campusID"] == campus_id and prog['programmeName'].startswith("Diploma"):
                                        campus_data[intakeName][campus_name]["Diploma"][prog["programmeID"]] = prog["programmeName"]
                                    elif(prog["campusID"] == campus_id and prog['programmeName'].startswith("Foundation")):
                                        campus_data[intakeName][campus_name]["Foundation"][prog["programmeID"]] = prog["programmeName"]
    except Exception as e:
        return str(e)

    finally:
        cursor.close()
    return campus_data

@app.route('/application/qualification')
def qualification():
    return render_template("Qualification.html")

@app.route('/application/assess', methods=['POST'])
def assess_qualification():
    id = session["appid"]
    spmObj = request.files["diploma"].read()
    diploma = request.files["degree"].read()
    if spmObj:
        data = scan_img(spmObj)
    else:
        data = ""
    if diploma:
        data2 = scan_img(diploma)
    else:
        data2 = ""
    spm_subjects = [
    "Bahasa Inggeris",
    "Mathematics",
    "Additional Mathematics",
    "Sains",
    "Chemistry",
    "Kimia",
    "Physics",
    "Ekonomi",
    "Prinsip Perakaunan",
    "Pendidikan Moral",
    "Sains Komputer",
    "Bahasa Cina",
    # Add more subjects here as needed
]
    cursor = db_conn.cursor(cursors.DictCursor)
    try:
        credits = 0
        allow = False
        status = "End"
        cursor.execute("SELECT apID, pc.programmeID, programmeType, ap.programmeCampusID FROM ApplicationProgramme ap " + 
                       "LEFT JOIN ProgrammeCampus pc ON ap.programmeCampusID = pc.programmeCampusID " +
                       "LEFT JOIN Programme p ON pc.programmeID = p.programmeID " +
                       "WHERE applicationID = %s", (id))
        choices = cursor.fetchall()

        # bm and sejarah must pass
        if("bahasa melayu" in data.lower() or "sejarah" in data.lower()):
            bm = data.lower().find("bahasa melayu")
            sj = data.lower().find("sejarah")

            if(data[bm:bm + len("bahasa melayu") + 2][-2:] < "G" and data[sj:sj + len("sejarah") + 2][-2:] < "G"):
                if(data[bm:bm + len("bahasa melayu") + 2][-2:] <= "C"):
                    credits += 1
                if(data[sj:sj + len("sejarah") + 2][-2:] <= "C"):
                    credits += 1
                allow = True
            else:
                allow = False

        for subject in spm_subjects:
            found = data.lower().find(subject.lower())
            if found > 0:
                if(data[found:found + len(subject) + 2][-2:] <= "C"):
                    credits += 1
        
        for choice in choices:
            tempCredits = credits



            
            if choice['programmeType'] == 'xDegree':
                if(status == "Approved"):
                    cursor.execute("UPDATE ApplicationProgramme SET apStatus = %s WHERE programmeCampusID = %s AND apID = %s", ("End", choice["programmeCampusID"], choice["apID"]))
                    db_conn.commit()
                    continue
                if allow:
                    if data == "":
                        flash("Please upload your SPM result.")
                        return redirect(url_for('qualification'))
                    cursor.execute("SELECT * FROM QualificationSubject WHERE programmeID = %s", choice['programmeID'])
                    qualifications = cursor.fetchall()
                    for qualification in qualifications:
                        found = data.lower().find(qualification["subjectName"].lower())
                        if(found > 0):
                            if(data[found:found + len(qualification["subjectName"]) + 2][-2:] <= qualification["grade"]):
                                credits += 1
                            else: 
                                status = "Rejected"
                    if(tempCredits < 5):
                        status = "Rejected"
                    else: 
                        status = "Approved"
                else:
                    status = "Rejected"
                cursor.execute("UPDATE ApplicationProgramme SET apStatus = %s WHERE programmeCampusID = %s AND apID = %s", (status, choice["programmeCampusID"], choice["apID"]))
                db_conn.commit()

            else:
                if data2 == "":
                    flash("Please upload your Diploma or Foundation Result.")
                    return redirect(url_for('qualification'))
                cursor.execute("SELECT * FROM QualificationSubject WHERE programmeID = %s", choice['programmeID'])
                qualifications = cursor.fetchall()
                acronyms = []
                for qualification in qualifications:
                    words = qualification["subjectName"].split()
                    acronyms.append("".join(word[0].upper() for word in words if word != "in"))

                for acronym in acronyms:
                    if(status == "Approved"):
                        cursor.execute("UPDATE ApplicationProgramme SET apStatus = %s WHERE programmeCampusID = %s AND apID = %s", ("End", choice["programmeCampusID"], choice["apID"]))
                        db_conn.commit()
                        continue                    
                    if(acronym in data2):
                        print(data2.find(acronym))
                        if("CGPA" in data2):
                            cgpa_positions = data2.rfind("CGPA")
                            if(data2[cgpa_positions:cgpa_positions + len("CGPA") + 7][-7:] >= "25000"):
                                status = "Rejected"
                                print(data2[cgpa_positions:cgpa_positions + len("CGPA") + 7][-7:] >= "25000")
                                print(data2[cgpa_positions:cgpa_positions + len("CGPA") + 7][-7:])
                            else:
                                status = "Approved"
                    else: 
                        status = "Rejected"
                    cursor.execute("UPDATE ApplicationProgramme SET apStatus = %s WHERE programmeCampusID = %s AND apID = %s", (status, choice["programmeCampusID"], choice["apID"]))
                    db_conn.commit()

            cursor.execute("UPDATE ApplicationProgramme SET apStatus = %s WHERE programmeCampusID = %s AND apID = %s", (status, choice["programmeCampusID"], choice["apID"]))
            db_conn.commit()
            
        appid = session['appid']
        cursor.execute("UPDATE Applications SET applicationStatus = %s WHERE applicationID = %s", ("Done", appid))
        db_conn.commit()

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return redirect(url_for('studhome'))


def scan_img(fileObj):
    # Mention the installed location of Tesseract-OCR in your system
    pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'
    #convert string data to numpy array
    file_bytes = np.fromstring(fileObj, np.uint8)
    # convert numpy array to image
    image = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
    # Reduce noise
    image = cv2.medianBlur(image, 3)

    # Perform OCR
    data = pytesseract.image_to_string(image, config='--psm 6')
    weird_symbols_and_words = r"[^A-Z0-9\s]"
    # Find all the matches for the regular expression
    matches = re.findall(weird_symbols_and_words, data)
    for match in matches:
        data = data.replace(match, "")
    data = data.split()
    data = ' '.join(data)

    # cv2.namedWindow("source", cv2.WINDOW_NORMAL)
    # cv2.imshow('source', image)
    cv2.waitKey()     

    return data

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

    return redirect(url_for("studhome"))


@app.route("/", methods=["GET", "POST"])
def Get_Programme():
    if session.get('loggedin') == False or session.get('loggedin') == None:
        session['loggedin'] = False 
    cursor = db_conn.cursor()
    if request.method == 'GET':
        query = "SELECT * FROM Programme ORDER BY programmeDuration"   
        cursor.execute(query)
    elif request.method == 'POST':
        likeStr = '%' + request.form["search"] + '%'
        query = "SELECT * FROM Programme WHERE programmeName LIKE %s ORDER BY programmeDuration"
        cursor.execute(query,likeStr)
    prog = cursor.fetchall()    
    cursor.close()
    return render_template('Programme.html', prog=prog)

@app.route("/programme/search=<progName>", methods=["POST"])
def Search_Programme(progName):
    cursor = db_conn.cursor()
    query = "SELECT * FROM Programme WHERE programmeName = %s% ORDER BY programmeDuration"
    cursor.execute(query,request.form["search"])    
    prog = cursor.fetchall()    
    cursor.close()
    return render_template('Programme.html', prog=prog)

@app.route("/progDetails/<progID>", methods=['GET', 'POST'])
def Get_Programme_Details(progID):
    if request.method == "GET":
        cursor = db_conn.cursor()
        progSql = "SELECT * FROM Programme WHERE ProgrammeID=%s"
        cursor.execute(progSql, (progID))
        prog = cursor.fetchall()
        courseSql = "SELECT Course.* FROM Course,ProgrammeCourse,Programme WHERE Programme.programmeID = ProgrammeCourse.programmeID AND ProgrammeCourse.courseCode = Course.courseCode AND Programme.programmeID=%s ORDER BY CourseName"
        cursor.execute(courseSql, (progID))
        course = cursor.fetchall()
        reqSql = "SELECT * FROM QualificationSubject WHERE programmeID=%s"
        cursor.execute(reqSql, (progID))
        tempReq = cursor.fetchall()
        grouped_data = defaultdict(list)
        progOvSql = "SELECT intakeYear,intakeMonth,programmeDuration,campusName FROM Programme,ProgrammeCampus,Intake,Campus WHERE Programme.programmeID = ProgrammeCampus.programmeID  AND Intake.IntakeID = ProgrammeCampus.intakeID AND Campus.campusID = ProgrammeCampus.campusID AND Programme.programmeID = %s"
        cursor.execute(progOvSql, (progID))
        ov = cursor.fetchall()
        for row in tempReq:
            group_key = row[3]
            grouped_data[group_key].append(row)
        cursor.close()
        return render_template('ProgDetails.html',progID=progID, prog=prog ,course=course, req=grouped_data,ov=ov)


@app.route("/progCompare/<progID>", methods=["GET", "POST"])
def Compare_Programme(progID):
    cursor = db_conn.cursor()    
    if request.method == 'GET':
        mainProg = "Select * from Programme WHERE programmeID = %s"
        cursor.execute(mainProg,(progID))
        mProg = cursor.fetchall()
        progListSql = "Select programmeName,programmeID from Programme WHERE programmeID != %s AND programmeType = %s"
        cursor.execute(progListSql,(progID,mProg[0][4]))
        progList = cursor.fetchall()
        # overview1
        progOvSql = "SELECT programmeName, intakeYear,intakeMonth,programmeDuration,campusName FROM Programme,ProgrammeCampus,Intake,Campus WHERE Programme.programmeID = ProgrammeCampus.programmeID  AND Intake.IntakeID = ProgrammeCampus.intakeID AND Campus.campusID = ProgrammeCampus.campusID AND Programme.programmeID = %s"
        cursor.execute(progOvSql, (progID))
        mOv = cursor.fetchall()
        progDict = {}
        for prog in mOv:
            if prog[0] not in progDict:
                progDict[prog[0]] = {"intake": [], "locations": []}
            progDict[prog[0]]["intake"].append(f"{prog[1]}/{prog[2]}")

            progDict[prog[0]]["locations"].append(prog[4])
            progDict[prog[0]]["duration"] = prog[3]
        progDict[mOv[0][0]]["intake"] = set(progDict[mOv[0][0]]["intake"])
        progDict[mOv[0][0]]["locations"] = set(progDict[mOv[0][0]]["locations"])

        # overview2
        progOvSql = "SELECT programmeName, intakeYear,intakeMonth,programmeDuration,campusName FROM Programme,ProgrammeCampus,Intake,Campus WHERE Programme.programmeID = ProgrammeCampus.programmeID  AND Intake.IntakeID = ProgrammeCampus.intakeID AND Campus.campusID = ProgrammeCampus.campusID AND Programme.programmeID = %s"
        cursor.execute(progOvSql, (progList[0][1]))
        mOv = cursor.fetchall()
        progDict1 = {}
        for prog in mOv:
            if prog[0] not in progDict1:
                progDict1[prog[0]] = {"intake": [], "locations": []}
            progDict1[prog[0]]["intake"].append(f"{prog[1]}/{prog[2]}")
            progDict1[prog[0]]["locations"].append(prog[4])
            progDict1[prog[0]]["duration"] = prog[3]
        progDict1[mOv[0][0]]["intake"] = set(progDict1[mOv[0][0]]["intake"])
        progDict1[mOv[0][0]]["locations"] = set(progDict1[mOv[0][0]]["locations"])
        combinedDict = {}
        combinedDict.update(progDict)
        combinedDict.update(progDict1)
        sortedDict = sorted(combinedDict.items(), key=lambda x: x[0])

        # compare requirement
        reqSql = "(SELECT DISTINCT programmeName,qualificationName,subjectName,grade FROM QualificationSubject, Programme WHERE QualificationSubject.programmeID = Programme.programmeID AND Programme.programmeID=%s)UNION(SELECT DISTINCT programmeName,qualificationName,subjectName,grade FROM QualificationSubject, Programme WHERE QualificationSubject.programmeID = Programme.programmeID AND Programme.programmeID=%s)ORDER BY ProgrammeName"
        cursor.execute(reqSql, (progID, progList[0][1]))
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
        reqSql = "(SELECT DISTINCT programmeName,qualificationName,subjectName,grade FROM QualificationSubject, Programme WHERE QualificationSubject.programmeID = Programme.programmeID AND Programme.programmeID=%s)UNION(SELECT DISTINCT programmeName,qualificationName,subjectName,grade FROM QualificationSubject, Programme WHERE QualificationSubject.programmeID = Programme.programmeID AND Programme.programmeID=%s)ORDER BY ProgrammeName"
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
                cursor.execute("SELECT * FROM LoginSession ORDER BY loginTime DESC limit %s, %s;",(row, rowperpage))
            else:
                cursor.execute(
                    "SELECT * FROM LoginSession WHERE ipAddress LIKE %s ORDER BY loginTime DESC limit %s, %s;",(searchValue,row,rowperpage))
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


@app.route("/admission/firstlogin", methods=["GET", "POST"])
def FirstLogin():
    return render_template("FirstLogin.html")


@app.route("/TempPage", methods=["GET", "POST"])
def TempPage():
    return render_template("TempPage.html")

@app.route("/admission/addenquiry", methods=["GET", "POST"])
def AddEnquiry():
    id = session["userid"]
    user_sql = "SELECT * FROM Account WHERE accountID=%s"
    try:
        cursor = db_conn.cursor(cursors.DictCursor)
        cursor.execute(user_sql, id)
        user = cursor.fetchone()
        return render_template(
            "AddEnquiry.html",
            name=user["fullName"],
            phone=user["handphoneNumber"],
            email=user["accEmail"],
        )
    except Exception as e:
        print(e)
    finally:
        cursor.close()


@app.route("/AddEnquiry", methods=["GET", "POST"])
def addEnquiry():
    id = session["userid"]
    topic = request.form.get("inputTopic")
    title = request.form.get("inputTitle")
    question = request.form.get("inputQuestion")
    file = request.files["inputFile"]

    try:
        malaysia_timezone = pytz.timezone("Asia/Kuala_Lumpur")
        malaysia_time = datetime.datetime.now().astimezone(malaysia_timezone)
        cursor = db_conn.cursor(cursors.DictCursor)
        cursor.execute(
            "INSERT INTO Enquiry (enquiryTopic, enquiryTitle, question, datetimeEnquire, enquiryStatus, enquiryAccountID)VALUES (%s, %s, %s, %s, %s, %s)",
            (topic, title, question, malaysia_time, "Pending Reply", id),
        )
        db_conn.commit()
        if file.filename != "":
            enquiryID = cursor.lastrowid
            path = "static/media/" + str(enquiryID) + "_" + malaysia_time.strftime("%Y%m%d_%H%M%S") + "_"+ file.filename
            file.save(os.path.join(path))
            cursor.execute(
                "UPDATE Enquiry SET enquiryImagePath=%s WHERE enquiryID=%s",
                (path, enquiryID),
            )
            db_conn.commit()
        flash(
            "Enquiry form has been submitted. Takes up to 3 working days to receive reply.",
            category="success",
        )
    except Exception as e:
        print(e)
    finally:
        cursor.close()

    return redirect(url_for("AddEnquiry"))


@app.route("/admission/enquirydetails", methods=["GET", "POST"])
def enquiryDetails():
    enquiryID = request.args.get("id")
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
    enquiryID = session["userid"]
    draw = request.form["draw"]
    row = int(request.form["start"])
    rowperpage = int(request.form["length"])
    searchValue = request.form["search[value]"]

    try:
        cursor = db_conn.cursor(cursors.DictCursor)

        ## Total number of records without filtering
        cursor.execute(
            "SELECT count(*) as allcount FROM Enquiry WHERE enquiryAccountID=%s",
            enquiryID,
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
    adminid = session["userid"]
    enquiryid = request.form.get("inputEnquiryID")
    feedback = request.form.get("inputQuestion")
    file = request.files["inputFile"]

    try:
        malaysia_timezone = pytz.timezone("Asia/Kuala_Lumpur")
        malaysia_time = datetime.datetime.now().astimezone(malaysia_timezone)
        cursor = db_conn.cursor(cursors.DictCursor)
        cursor.execute(
            "UPDATE Enquiry SET responseAccountID=%s, response=%s, datetimeResponse=%s, enquiryStatus=%s WHERE enquiryID=%s",
            (adminid, feedback, malaysia_time, "Completed", enquiryid),
        )
        db_conn.commit()
        if file.filename != "":
            path = "static/media/" + str(enquiryid) + "_" + malaysia_time.strftime("%Y%m%d_%H%M%S") + "_" + file.filename
            file.save(os.path.join(path))
            cursor.execute(
                "UPDATE Enquiry SET responseImagePath=%s WHERE enquiryID=%s",
                (path, enquiryid),
            )
            db_conn.commit()
        flash("A response has been submitted.", category="success")
    except Exception as e:
        print(e)
    finally:
        cursor.close()

    return redirect(url_for("adminEnquiryDetails", id=enquiryid))


@app.route("/admin/enquirydetails", methods=["GET", "POST"])
def adminEnquiryDetails():
    enquiryID = request.args.get("id")
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
        cursor.execute("SELECT count(*) as allcount FROM Enquiry")
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
    id = session["userid"]
    logout_sql = "UPDATE LoginSession SET logoutTime=%s WHERE accountID=%s"
    try:
        cursor = db_conn.cursor(cursors.DictCursor)
        malaysia_timezone = pytz.timezone("Asia/Kuala_Lumpur")
        malaysia_time = datetime.datetime.now().astimezone(malaysia_timezone)
        cursor.execute(logout_sql, (malaysia_time, id))
        db_conn.commit()
        session["loggedin"] = False
        session.pop("userid", None)
        session.pop("username", None)

        return redirect("/")
    except Exception as e:
        print(e)
    finally:
        cursor.close()
    return redirect("/")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
