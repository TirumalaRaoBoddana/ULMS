from flask import Flask,render_template, request
from flask_mysqldb import MySQL
from flask import jsonify
import hashlib
from datetime import date
from datetime import datetime
import face_recognition
import numpy as np
import pandas as pd
import base64
import os
import requests
import requests
from email.message import EmailMessage
import ssl
import smtplib
IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'images')
os.makedirs(IMAGE_DIR, exist_ok=True)
def compare_images(captured_image,downloaded_image):
    image1 = face_recognition.load_image_file(captured_image)
    image2 = face_recognition.load_image_file(downloaded_image)
    face_encoding1 = face_recognition.face_encodings(image1)
    face_encoding2 = face_recognition.face_encodings(image2)

    if len(face_encoding1) == 0 or len(face_encoding2) == 0:
        return False
    match = face_recognition.compare_faces([face_encoding1[0]], face_encoding2[0])
    return match[0]
def download_image(url, filename='downloaded_image.jpg'):
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(IMAGE_DIR, filename), 'wb') as f:
            f.write(response.content)
        print(f"Image downloaded and saved as '{filename}'")
    else:
        print(f"Failed to download image from '{url}'")
def sendEmail(to,subject, body):
    email_sender='universityleavemanagement@gmail.com'
    email_password='krvt qyac zkuw mvhe'
    email_receiver=to
    subject=subject
    body=body
    em=EmailMessage()
    em['From']=email_sender
    em['To']=email_receiver
    em['subject']=subject
    em.set_content(body)
    context=ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
        smtp.login(email_sender,email_password)
        smtp.sendmail(email_sender,email_receiver,em.as_string())
def getUserDetails(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM details WHERE id = %s", (id,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            user_details = {
                "id": user[0],
                "name":user[1],
                 "gender": user[2],
                "dob":user[3],
                "mobile": user[4],
                "mail":user[5], 
                "branch": user[6],
                "parentname":user[7],  
                "address":user[8],     
            }
        return user_details
    except Exception as e:
        return "Error Occured in fetching details"
def fetch_outings_data():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM requestoutings")
        outings = cursor.fetchall()
        cursor.close()
        return outings
    except Exception as e:
        print("Error fetching outings data:", e)
        return []
def fetch_leaves_data():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM requestleave")
        leaves = cursor.fetchall()
        cursor.close()
        return leaves
    except Exception as e:
        print("Error fetching leaves data:", e)
        return []
app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = 'thiru@1234'
app.config["MYSQL_DB"] = 'rgukt'
mysql = MySQL(app)
@app.route("/")
def homePage():
    return render_template("index.html")
@app.route('/admin')
def admin():
    return render_template("admin.html")
@app.route("/security")
def security():
    return render_template("security.html")
@app.route('/index')
def index():
    return render_template('index.html')
@app.route("/login", methods=["POST"])
def login():
    id = request.form["idNo"]
    password = request.form["password"]
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT SHA2(%s, 256)", (password,))
        hashed_password = cursor.fetchone()[0]
        cursor.execute("SELECT hashed_password FROM students WHERE id = %s", (id,))
        stored_password = cursor.fetchone()
        cursor.close()
        if stored_password and stored_password[0] == hashed_password:
            details=getUserDetails(id)
            return render_template("main.html",idnumber=details["id"],name=details["name"],gender=details["gender"],DOB=details["dob"],mobile=details["mobile"],mail=details["mail"],branch=details["branch"],ParentName=details["parentname"],Address=details["address"])
        else:
            return "<script>alert('invalid Id or Password')</script>"
    except Exception as e:
        return f"Login failed. Error: {str(e)}"
@app.route("/submitdata", methods=["POST"])
def submitdata():
    if request.method == "POST":
        dropdown_value = request.form['dropdown']
        idnum=request.form["idnumber"]
        name=request.form["name"]
        gender=request.form["gender"]
        mobile=request.form["mobile"]
        branch=request.form["branch"]
        parentname=request.form["parentname"]
        address=request.form["address"]
        if dropdown_value == 'outing':
            out_time = request.form['outtime']
            in_time = request.form['intime']
            reason = request.form['outingreason']
            if(reason!=""):
                try:
                    cursor = mysql.connection.cursor()
                    query = "INSERT INTO requestoutings(id, name, gender, branch, mobile, parent_name, address, outtime, intime, date, reason) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    data = (idnum, name, gender, branch, mobile, parentname, address, out_time, in_time,date.today(),reason)
                    cursor.execute(query, data)
                    mysql.connection.commit() 
                except Exception as e:
                    return "<script>alert('Only one request Will be Accepted in One Day');</script>"
                finally:
                    cursor.close() 
                return render_template('print.html',type="outingform",id=idnum,name=name,gender=gender,branch=branch,mobile=mobile,parentname=parentname,address=address,outtime=out_time,intime=in_time,reason=reason)
            else:
                return "<script>alert('Reason should not be Empty');</script>"
        elif dropdown_value == 'leave':
            out_date = request.form['outdate']
            in_date = request.form['indate']
            reason = request.form['leavereason'] 
            try:
                cursor = mysql.connection.cursor()
                query = "INSERT INTO requestleave(id, name, gender, branch, mobile, parent_name, address, outdate, indate,reason) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                data = (idnum, name, gender, branch, mobile, parentname, address, out_date, in_date,reason)
                cursor.execute(query, data)
                mysql.connection.commit() 
            except Exception as e:
                return "<script>alert('Only one request Will be Accepted in One Day')</script>"
            finally:
                cursor.close() 
            return render_template("print.html",type="leaveform",id=idnum,name=name,gender=gender,branch=branch,mobile=mobile,parentname=parentname,address=address,outdate=out_date,indate=in_date,reason=reason)
    else:
        return "Form submission failed"
@app.route("/loginadmin", methods=["POST"])
def loginadmin():
    if request.method == "POST":
        username = request.form["name"]
        mail = request.form["mail"]
        password = request.form["password"]
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT SHA2(%s, 256)", (password,))
            hashed_password = cursor.fetchone()[0] 
            cursor.execute("SELECT * FROM admin WHERE username = %s AND email = %s", (username.strip(), mail.strip()))
            admin_row = cursor.fetchone()  
            if admin_row is not None and username==admin_row[0] and mail==admin_row[1] and hashed_password == admin_row[2]:  
                return render_template("data.html")
            else:
                mysql.connection.commit()
                return "Wrong password or username"
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
    else:
        return "Login Failed"
@app.route("/loginsecurity",methods=["POST"])
def loginsecurity():
    if request.method == "POST":
        cursor = None  
        try:
            username = request.form["name"]
            mail = request.form["mail"]
            password = request.form["password"]
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT SHA2(%s, 256)", (password,))
            hashed_password = cursor.fetchone()[0] 
            
            cursor.execute("SELECT * FROM security WHERE username = %s AND email = %s", (username.strip(), mail.strip()))
            admin_row = cursor.fetchone()  
            
            if admin_row is not None and username == admin_row[0] and mail == admin_row[1] and hashed_password == admin_row[2]: 
                return render_template("securitydata.html")
            else:
                return "Invalid username or password"
        except Exception as e:
            return "Database error: " + str(e)
        finally:
            if cursor:
                cursor.close()
    else:
        return "Login Failed"
@app.route("/fetch_data")
def fetch_data():
    outings = fetch_outings_data()
    leaves = fetch_leaves_data()
    return jsonify(outings=outings, leaves=leaves)
@app.route("/accept_request", methods=["POST"])
def accept_request():
    if request.method == 'POST':
        data = request.json
        id = data.get("id")
        type = data.get('type')
        if type == "outing":
            try:
                cursor = mysql.connection.cursor()
                cursor.execute("SELECT * FROM requestoutings WHERE id = %s", (id,))
                outing_data = cursor.fetchone()
                mysql.connection.commit()
                cursor.execute("INSERT INTO outingsOut(id, name, gender, branch, mobile, parent_name, address, outtime, intime, date, reason) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", outing_data)
                mysql.connection.commit()
                cursor.execute("DELETE FROM requestoutings WHERE id = %s", (id,))
                mysql.connection.commit()
                # Send email for confirmation of the outing request by authority
                to = id.lower() + "@rguktn.ac.in"
                subject = "Outing Request Accepted!!"
                body = "Outing Request with id number {} is accepted. Thanks For using ULMS. Have a Nice Day!!".format(id)
                sendEmail(to, subject, body)
            except Exception as e:
                return str(e)
            finally:
                cursor.close()
        elif type == "leave":
            try:
                cursor = mysql.connection.cursor()
                cursor.execute("SELECT * FROM requestleave WHERE id = %s", (id,))
                leave_data = cursor.fetchone()
                cursor.execute("INSERT INTO leaveout (id, name, gender, branch, mobile, parent_name, address, outdate, indate, reason) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", leave_data)
                cursor.execute("DELETE FROM requestleave WHERE id = %s", (id,))
                mysql.connection.commit()
                to = id.lower() + "@rguktn.ac.in"
                subject = "Leave Request Accepted!!"
                body = "Leave Request with id number {} is accepted. Thanks For using ULMS. Happy Journey".format(id)
                sendEmail(to, subject, body)
            except Exception as e:
                return str(e)
            finally:
                if cursor:
                    cursor.close()
        else:
            return jsonify({"message": "Some error occurred"}), 200
        
        return jsonify({'message': f'Request with ID {id} accepted successfully'}), 200
    else:
        return jsonify({'error': 'Method not allowed'}), 405
@app.route("/reject_request",methods=["POST"])
def reject_request():
    if(request.method=='POST'):
        data=request.json
        id=data.get("id")
        type=data.get('type')
        if(type=="outing"):
            try:
                cursor=mysql.connection.cursor()
                cursor.execute("delete from requestoutings where id=%s",(id,))
                mysql.connection.commit()
                to=id.lower()+"@rguktn.ac.in"
                subject="Outing Request Rejected!!"
                body="Outing Request with id number {} is Rejected by the authority.For any queries contact the Authourity".format(id)
                sendEmail(to,subject,body)
            except Exception as e:
                return str(e)
            finally:
                cursor.close()
        else:
            try:
                cursor=mysql.connection.cursor()
                cursor.execute("delete from requestleave where id=%s",(id,))
                mysql.connection.commit()
                to=id.lower()+"@rguktn.ac.in"
                subject="Leave Request Rejected!!"
                body="Outing Request with id number {} is Rejected by the authority.For any queries contact the Authourity".format(id)
                sendEmail(to,subject,body)
            except Exception as e:
                return str(e)
            finally:
                cursor.close()
        return jsonify({'message': f'Request with ID {id} accepted successfully'}), 200
    else:
        return jsonify({'error': 'Method not allowed'}), 405
@app.route("/outingOut")
def outingOut():
    return render_template("securitydata.html")
@app.route("/outingIn")
def outingIn():
    return render_template("outingIn.html")
@app.route("/leaveOut")
def leaveOut():
    return render_template("leaveOut.html")
@app.route("/leaveIn")
def leaveIn():
    return render_template("leaveIn.html")
@app.route('/outingsAndleaves')
def outingsAndleaves():
    return render_template('OutingsAndLeaves.html')
@app.route("/verify_outing_out", methods=["POST"])
def verify_outing_out():
    if request.method == "POST":
        try:
            image_data = request.form['image']
            id_number = request.form['idNumber']
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM outingsout WHERE id = %s", (id_number,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                filename = 'captured_image.png'
                with open(os.path.join(IMAGE_DIR, filename), 'wb') as f:
                    f.write(base64.b64decode(image_data.split(',')[1]))
                download_image("https://intranet.rguktn.ac.in/SMS/usrphotos/user/{}.jpg".format(id_number))
                captured_image = "images/captured_image.png"
                downloaded_image = "images/downloaded_image.jpg"
                if compare_images(captured_image, downloaded_image):
                    print(len(result))
                    cursor=mysql.connection.cursor()
                    cursor.execute("INSERT INTO outingsIn(id, name, gender, branch, mobile, parent_name, address, outtime, intime, date, reason) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", tuple(result[1:]))
                    mysql.connection.commit()
                    cursor.execute("DELETE FROM outingsout WHERE id = %s", (id_number,))
                    mysql.connection.commit()
                    cursor.close()
                    return jsonify({'message': 'Success'})
                else:
                    return jsonify({'message': 'Failure'})
            else:
                return jsonify({'message': 'Outing record not found'})
        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        return jsonify({'message': 'Invalid request method'})
@app.route("/verify_outing_in", methods=["POST"])
def verify_outing_in():
    if request.method == "POST":
        try:
            image_data = request.form['image']
            id_number = request.form['idNumber']
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM outingsin WHERE id = %s", (id_number,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                filename = 'captured_image.png'
                with open(os.path.join(IMAGE_DIR, filename), 'wb') as f:
                    f.write(base64.b64decode(image_data.split(',')[1]))
                download_image("https://intranet.rguktn.ac.in/SMS/usrphotos/user/{}.jpg".format(id_number))
                captured_image = "images/captured_image.png"
                downloaded_image = "images/downloaded_image.jpg"
                if compare_images(captured_image, downloaded_image):
                    print(len(result))
                    cursor=mysql.connection.cursor()
                    cursor.execute("INSERT INTO outings(id, name, gender, branch, mobile, parent_name, address, outtime, intime, date, reason) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", tuple(result[1:]))
                    mysql.connection.commit()
                    cursor.execute("DELETE FROM outingsin WHERE id = %s", (id_number,))
                    mysql.connection.commit()
                    cursor.close()
                    return jsonify({'message': 'Success'})
                else:
                    return jsonify({'message': 'Failure'})
            else:
                return jsonify({'message': 'Outing record not found'})
        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        return jsonify({'message': 'Invalid request method'})
@app.route("/verify_leave_out", methods=["POST"])
def verify_leave_out():
    if request.method == "POST":
        try:
            image_data = request.form['image']
            id_number = request.form['idNumber']
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM leaveout WHERE id = %s", (id_number,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                filename = 'captured_image.png'
                with open(os.path.join(IMAGE_DIR, filename), 'wb') as f:
                    f.write(base64.b64decode(image_data.split(',')[1]))
                download_image("https://intranet.rguktn.ac.in/SMS/usrphotos/user/{}.jpg".format(id_number))
                captured_image = "images/captured_image.png"
                downloaded_image = "images/downloaded_image.jpg"
                if compare_images(captured_image, downloaded_image):
                    cursor=mysql.connection.cursor()
                    print(tuple(result[1:]))
                    cursor.execute("INSERT INTO leavein(id, name, gender, branch, mobile, parent_name, address, outdate, indate, reason) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",tuple(result[1:]))
                    mysql.connection.commit()
                    cursor.execute("DELETE FROM leaveout WHERE id = %s", (id_number,))
                    mysql.connection.commit()
                    cursor.close()
                    return jsonify({'message': 'Success'})
                else:
                    return jsonify({'message': 'Failure'})
            else:
                return jsonify({'message': 'Outing record not found'})
        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        return jsonify({'message': 'Invalid request method'})
    
@app.route("/verify_leave_in", methods=["POST"])
def verify_leave_in():
    if request.method == "POST":
        try:
            image_data = request.form['image']
            id_number = request.form['idNumber']
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM leavein WHERE id = %s", (id_number,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                filename = 'captured_image.png'
                with open(os.path.join(IMAGE_DIR, filename), 'wb') as f:
                    f.write(base64.b64decode(image_data.split(',')[1]))
                download_image("https://intranet.rguktn.ac.in/SMS/usrphotos/user/{}.jpg".format(id_number))
                captured_image = "images/captured_image.png"
                downloaded_image = "images/downloaded_image.jpg"
                if compare_images(captured_image, downloaded_image):
                    cursor=mysql.connection.cursor()
                    cursor.execute("INSERT INTO leaves(id, name, gender, branch, mobile, parent_name, address, outdate, indate, reason) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",tuple(result[1:]))
                    mysql.connection.commit()
                    cursor.execute("DELETE FROM leavein WHERE id = %s", (id_number,))
                    mysql.connection.commit()
                    cursor.close()
                    return jsonify({'message': 'Success'})
                else:
                    return jsonify({'message': 'Failure'})
            else:
                return jsonify({'message': 'Outing record not found'})
        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        return jsonify({'message': 'Invalid request method'})
@app.route('/fetch_Outing_out_data')
def fetch_Outing_out_data():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM outingsOut")
        outings = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print("Error fetching outings data:", e)
    return jsonify(outings=outings)
@app.route('/fetch_Outing_in_data')
def fetch_Outing_in_data():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM outingsin")
        outings = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print("Error fetching outings data:", e)
    return jsonify(outings=outings)
@app.route('/fetch_Leave_out_data')
def fetch_Leave_out_data():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM leaveOut")
        leaves = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print("Error fetching leaves data:", e)
    return jsonify(leaves=leaves)
@app.route('/fetch_Leave_in_data')
def fetch_Leave_in_data():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM leavein")
        leaves = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print("Error fetching leaves data:", e)
    return jsonify(leaves=leaves)
@app.route('/fetch_leaves_data')
def fetch_leave_data():
    try:
        cursor=mysql.connection.cursor()
        cursor.execute("select * from leaves")
        leaves=cursor.fetchall()
        cursor.close()
    except Exception as e:
        print("Error fetching leaves data:", e)
    return leaves
@app.route('/fetch_outings_data')
def fetch_outing_data():
    try:
        cursor=mysql.connection.cursor()
        cursor.execute("select * from outings")
        outings=cursor.fetchall()
        cursor.close()
    except Exception as e:
        print("Error fetching leaves data:", e)
    return outings
@app.route("/fetch_outings_leaves")
def fetch_outings_leaves():
    outings = fetch_outing_data()
    leaves = fetch_leave_data()
    return jsonify(outings=outings, leaves=leaves)
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=9000, threaded=True)