from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from . import mydb  
import cv2
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .pwd import genpwd
from .myobjdetect import search_video_for_object
from datetime import datetime
#it has a bunch of urls defined in it
auth = Blueprint('auth', __name__)
# Home page 
@auth.route('/home')
def home():
    if 'loggedin' in session:
        return render_template("home.html")
    else:
        flash("You may be logged out/ You may not have logged in yet Please login to enter", category="error")
        return redirect(url_for("auth.login"))
# Log In Page
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Userid=request.form.get('Userid')
        password=request.form.get('password')
        mycursor=mydb.cursor();
        mycursor.execute("select userid,passwd, roleid, email from Users where userid=%s", (Userid,))
        account=mycursor.fetchone()
        mycursor.close()
        if account:
                print("in account")
                if password==account[1]:
                    session['loggedin'] = True
                    session['userid'] = account[0]
                    session['roleid'] = account[2]
                    session['email'] = account[3]
                    return redirect(url_for('auth.home'))
                else:
                    flash('Incorrect password, try again.', category='error')
        else:
            flash('User doesn\'t exist.', category='error')
    return render_template("Log In.html")

@auth.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        Userid=request.form.get("Userid")
        mycurs=mydb.cursor();
        mycurs.execute("select userid,passwd, email from Users where userid=%s", (Userid,))
        account=mycurs.fetchone()
        mycurs.close()
        if account:
                mycursor=mydb.cursor();
                Password=genpwd()
                datetimeob = datetime.now()
                mycursor.execute("update Users set passwd=%s, updatedby=%s, updatedtime=%s where userid=%s", (Password, Userid, datetimeob, Userid))
                mydb.commit()
                mycursor.close();
                mail_content = """Hello {},\nOn your request, your password has been reset to '{}'. Kindly relogin using this password. You can change your password by clicking on change password after logging into our website.""".format(Userid, Password)
                sender_address = 'emaildemomy414@gmail.com'
                sender_pass = 'tbbzkewgvcvkxoeu'
                receiver_address = account[2]
                message = MIMEMultipart()
                message['From'] = sender_address
                message['To'] = receiver_address
                message['Subject'] = 'Regarding Password for Lost and Found Website'   
                message.attach(MIMEText(mail_content, 'plain'))
                sess = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
                sess.starttls() #enable security
                sess.login(sender_address, sender_pass)
                text = message.as_string()
                sess.sendmail(sender_address, receiver_address, text)
                sess.quit()
                flash('Password reset Successful. Check your college e-mail id for your Password and relogin here!', category='success')
                return redirect(url_for('auth.login'))
        else:
            mycurs.close();
            flash('User doesn\'t exist.', category='error')
    return render_template("Forgot Password.html")

# Sign up  page
@auth.route('/create', methods=["GET", "POST"])
def create():
    if(request.method=='POST'):
        userid=request.form.get('Userid')
        passwd=request.form.get('password1')
        cpasswd=request.form.get('password2')
        fullname=request.form.get('fullname')
        email = request.form.get('email')
        contactno=request.form.get('contact')
        roleid=2301
        mycursor=mydb.cursor()
        mycursor.execute("select userid from Users where userid=%s", (userid,))
        user=mycursor.fetchone()
        mycursor.execute("select email from Users where userid=%s", (email,))
        Email = mycursor.fetchone()
        now = datetime.now()
        if(user):
            flash('User already exists', category='error')
            mycursor.close()
            return render_template("signup.html")
        if(Email):
            flash('This email is currently being used by someone', category='error')
            mycursor.close()
            return render_template("signup.html")
        if not (email.endswith("@student.nitandhra.ac.in") or email.endswith("@faculty.nitandhra.ac.in")):
            flash("Your email is not valid.", category='error')
            mycursor.close()
            return render_template("signup.html")
        if(" " in email):
            flash("Your email is not valid.", category='error')
            mycursor.close()
            return render_template("signup.html")
        if(passwd != cpasswd):
            flash('ALmost there! New Password and Confirm Password must be same', category='error')
            mycursor.close()  
            return render_template("signup.html")
        mycursor.execute("insert into Users(userid, passwd, fullname, email, contactno, roleid, createdby, createdtime) values (%s, %s, %s, %s, %s, %s, %s, %s)",(userid, passwd, fullname, email, contactno, roleid, userid, now))
        mydb.commit()
        flash("Account created", category='success')
        mycursor.close()
        return redirect(url_for('auth.login'))
    return render_template("signup.html")

# Change Password Page
@auth.route('/change', methods=['GET', 'POST'])
def change():
    if 'loggedin' in session:
        if request.method=='POST':
            Userid=session['userid']
            Password1=request.form.get("Password1")
            Password2=request.form.get("Password2")
            mycur=mydb.cursor()
            mycur.execute("select passwd from Users where userid=%s", (Userid,))
            account=mycur.fetchone()
            Oldpassword=account[0]
            if (len(Password1) < 8 or len(Password1) > 8):
                flash('Password must be of 8 characters', category='error')
            
            elif(Password1 != Password2):
                flash('New Password and Confirm Password both must be same', category='error')
            
            elif(Password1 == Oldpassword):
                flash('New Password and Old Password should not be same. Change to another password', category='error')
            else:
                datetimeob = datetime.now()
                mycur.execute("update Users set passwd=%s, updatedby=%s, updatedtime=%s where userid=%s", (Password1, Userid, datetimeob, Userid))
                mydb.commit()
                mycur.close();
                flash('Successfully changed your Password', category='success')
                return redirect(url_for('auth.home'))
        return render_template("Change Password.html")
    else:
        flash("You may be logged out/ You may not have logged in yet Please login to enter", category="error")
        return redirect(url_for('auth.login'))

# Logging out
@auth.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('roleid', None)
    session.pop('email', None)
    return redirect(url_for('auth.login'))

# Reporting lost item
@auth.route('/reportlost', methods=['GET', 'POST'])
def reportlost():
    if 'loggedin' in session:
        if request.method=='POST':
            reportedby=session['userid']
            obj = request.form['Object']
            Lostat = request.form['lostat']
            Lostdate = request.form['lostdate']
            Losttime= request.form['losttime']
            descrip = request.form['description']
            brand="NULL"
            color="NULL"
            size="NULL"
            remarks="NULL"
            if 'Brand' in request.form:
                brand=request.form['Brand']
            if 'Color' in request.form:
                color=request.form['Color']
            if 'Size' in request.form:
                size=request.form['Size']
            if 'remarks' in request.form:
                remarks=request.form['remarks']
            datetimeob=datetime.now()
            selected_date = datetime.strptime(Lostdate, '%Y-%m-%d')
            selected_time = datetime.strptime(Losttime, '%H:%M')
            selected_datetime = datetime.combine(selected_date.date(), selected_time.time())
            if selected_datetime > datetimeob:
                flash("Lost Date and time exceeded present date and time. Kindly check", category='error')
            else:
                mycur = mydb.cursor()
                mycur.execute("select locationid from locations where location=%s", (Lostat,))
                Location = mycur.fetchone()
                location=Location[0]
                mycur.execute("insert into lostobinfo(object, size, brand, color, lostdate, losttime,description, remarks, locationid, reportedby, reportedtime) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(obj, size, brand, color, Lostdate, Losttime, descrip, remarks, location, reportedby, datetimeob))
                mydb.commit()
                mycur.close()
                flash('Lost item reported Successfully', category='success')
                return redirect(url_for('auth.home'))
        return render_template("report lost.html")
    else:
        flash("You may be logged out/ You may not have logged in yet Please login to enter", category="error")
        return redirect(url_for('auth.login'))
    
    
    # Search in CCTV videos page
@auth.route('/searchvideo', methods=['GET', 'POST'])
def searchvideo():
    if 'loggedin' in session:
        if request.method=='POST':
            Userid=session['userid']
            obj = request.form['Object']
            session['Object'] = obj
            Lostat = request.form['lostat']
            Lostat=int(Lostat)
            session['lostat'] = Lostat
            Lostdate = request.form['lostdate'] 
            session ['lostdate'] = Lostdate
            Losttime= request.form['losttime']
            session['losttime'] = Losttime
            descrip = request.form['description']
            brand="NULL"
            color="NULL"
            size="NULL"
            if 'Brand' in request.form:
                brand=request.form['Brand']
            if 'Color' in request.form:
                color=request.form['Color']
            if 'Size' in request.form:
                size=request.form['Size']
            mycur = mydb.cursor()
            location=Lostat
            mycur.execute("select lostid from lostobinfo where object=%s and color=%s and brand=%s and size=%s and lostdate=%s and losttime=%s and  locationid=%s and reportedby=%s ",( obj,color, brand, size, Lostdate, Losttime, location, Userid))
            lost=mycur.fetchone()
            mycur.close()
            if(lost):
                return redirect(url_for("auth.res"))
            else:
                flash("No Lost report present", category="error")
        return render_template("search in videos.html")
    else:
        flash("You may be logged out/ You may not have logged in yet Please login to enter", category="error")
        return redirect(url_for('auth.login'))
    
@auth.route('/res', methods=["GET", "POST"])
def res():
    obj = session['Object']
    lostat=session['lostat']
    losttime=session['losttime']
    lostat=session['lostat']
    mycursor = mydb.cursor();
    mycursor.execute("select video_link from cctv where locationid=%s and starttime<= %s and endtime > %s", (lostat, losttime, losttime))
    res = mycursor.fetchone()
    image_data = cv2.imread("notfound.jpg", cv2.IMREAD_ANYCOLOR)
    if (res):
        link = res[0]
        mycursor.close()
        image_data = search_video_for_object(link, obj.lower(), 0.1)
    else:
        image_data = search_video_for_object("website/static/videos/input_video1.mp4", obj.lower(), 0.1)
        mycursor.close()
    success, encoded_image = cv2.imencode('.jpg', image_data)
    if not success:
        return "Failed to encode image data"
    encoded_image_bytes = encoded_image.tobytes()
    encoded_image_b64 = base64.b64encode(encoded_image_bytes).decode('utf-8')
    return render_template('result.html', image_data=encoded_image_b64)
    
# Reporting found items page
@auth.route('/reportfound', methods=['GET', 'POST'])
def reportfound():
    if 'loggedin' in session:
        if request.method=='POST':
            Userid=session['userid']
            obj = request.form['Object']
            Foundat = request.form['foundat']
            Founddate = request.form['founddate']
            Foundtime= request.form['foundtime']
            descrip = request.form['description']
            brand="NULL"
            color="NULL"
            size="NULL"
            remarks="NULL"
            Collect = request.form['collect']
            if 'Brand' in request.form:
                brand=request.form['Brand']
            if 'Color' in request.form:
                color=request.form['Color']
            if 'Size' in request.form:
                size=request.form['Size']
            if 'remarks' in request.form:
                remarks=request.form['remarks']          
            datetimeob=datetime.now()
            selected_date = datetime.strptime(Founddate, '%Y-%m-%d')
            selected_time = datetime.strptime(Foundtime, '%H:%M')
            selected_datetime = datetime.combine(selected_date.date(), selected_time.time())
            if selected_datetime > datetimeob:
                flash("Found Date and time exceeded present date and time. Kindly check", category='error')
            else:
                mycur = mydb.cursor()
                mycur.execute("select locationid from locations where location=%s", (Foundat,))
                Location = mycur.fetchone()
                location=Location[0]
                mycur.execute("insert into foundobinfo(object, size, brand, color, founddate, foundtime,description, remarks, locationid, collectfrom, reportedby, reportedtime) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(obj, size, brand, color, Founddate, Foundtime, descrip, remarks, location, Collect,Userid, datetimeob))
                mydb.commit()
                mycur.close()
                flash(' Found item reported Successfully', category='success')
                return redirect(url_for('auth.home'))
        return render_template("Report found.html")
    else:
        flash("You may be logged out/ You may not have logged in yet Please login to enter", category="error")
        return redirect(url_for('auth.login'))
    
    
@auth.route('/searchfound', methods=['GET', 'POST'])
def searchfound():
    if 'loggedin' in session:
        mycursor = mydb.cursor()
        Headings = ['Object Name', 'Reported By', 'Found Date' , 'Status', 'Found Time', 'Size', 'Brand', 'Color', 'Description', 'Remarks', 'Collect from', 'Found Location', 'Returned to', 'Reported time']
        headings=['Object Name', 'Reported By', 'Found date', 'Status', 'View', 'Update']
        if request.method=='POST':
            searcher=request.form.get('Search')
            searchob=request.form.get('searcher')
            if(searcher == "1"):
                mycursor.execute("select foundid, object, reportedby, founddate,  objstatus, foundtime, size, brand, color, description, remarks, collectfrom, location, returnedto, reportedtime from foundobinfo f join locations l on f.locationid=l.locationid where object=%s",(searchob,))
                sdata=mycursor.fetchall()
            elif(searcher == "2"):
                mycursor.execute("select foundid, object, reportedby, founddate,  objstatus, foundtime, size, brand, color, description, remarks, collectfrom, location, returnedto, reportedtime from foundobinfo f join locations l on f.locationid=l.locationid where founddate=%s",(searchob,))
                sdata=mycursor.fetchall()
            elif(searcher== "3"):
                mycursor.execute("select foundid, object, reportedby, founddate,  objstatus, foundtime, size, brand, color, description, remarks, collectfrom, location, returnedto, reportedtime from foundobinfo f join locations l on f.locationid=l.locationid where reportedby=%s",(searchob,))
                sdata=mycursor.fetchall()
            else:
                mycursor.execute("select foundid, object, reportedby, founddate,  objstatus, foundtime, size, brand, color, description, remarks, collectfrom, location, returnedto, reportedtime from foundobinfo f join locations l on f.locationid=l.locationid where objstatus=%s",(searchob,))
                sdata=mycursor.fetchall()
            
        else:
            mycursor.execute("select foundid, object, reportedby, founddate,  objstatus, foundtime, size, brand, color, description, remarks, collectfrom, location, returnedto, reportedtime from foundobinfo f join locations l on f.locationid=l.locationid ")
            sdata = mycursor.fetchall()
        if(sdata):
            return render_template("search found.html", headings=headings, sdata=sdata, Headings=Headings)
        else:
            flash("No records found", category='error')
            return render_template("search found.html", headings=None, sdata=None, Headings=None)
    else:
        flash("You may be logged out/ You may not have logged in yet Please login to enter", category="error")
        return redirect(url_for('auth.login'))
    
@auth.route('/update', methods=['GET', 'POST'])
def update():
    Object = request.form.get('Object Name')
    foundid=request.form.get('foundid')
    status = request.form.get('Status')
    description = request.form.get('Description')
    if(description):
        pass
    else:
        description = 'NULL'
    remarks = request.form.get('Remarks')
    if(remarks):
        pass
    else:
        remarks = 'NULL'
    collectfrom = request.form.get('Collect from')
    updatedtime=datetime.now()

    returnedto = request.form.get('returnedto')
    mycursor = mydb.cursor()
    if(returnedto):
        returnedtime=datetime.now()
        mycursor.execute("select userid, email from Users where userid=%s", (returnedto,))
        found=mycursor.fetchone()
        if(found and returnedto != session['userid']):
            mycursor.execute("update foundobinfo set objstatus=%s, description=%s, remarks=%s , collectfrom=%s, returnedto=%s, returnedby =%s, returnedtime=%s, updatedby = %s, updatedtime=%s where foundid=%s", (status, description, remarks, collectfrom, returnedto, session['userid'], returnedtime, session['userid'],updatedtime, foundid))
            mydb.commit()
            mail_content = """Hello {},\n\tYou have collected your item '{}' from "{}". If this info is not correct please contact the {}'s email {} """.format(returnedto, Object, session['userid'], session['userid'], session['email'])
            sender_address = 'emaildemomy414@gmail.com'
            sender_pass = 'tbbzkewgvcvkxoeu'
            receiver_address = found[1]
            message = MIMEMultipart()
            message['From'] = sender_address
            message['To'] = receiver_address
            message['Subject'] = 'Regarding Claiming of an item'   
            message.attach(MIMEText(mail_content, 'plain'))
            sess = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
            sess.starttls() 
            sess.login(sender_address, sender_pass)
            text = message.as_string()
            sess.sendmail(sender_address, receiver_address, text)
            sess.quit()
            sender_address = 'emaildemomy414@gmail.com'
            sender_pass = 'tbbzkewgvcvkxoeu'
            receiver_address = session['email']
            messages = MIMEMultipart()
            messages['From'] = sender_address
            messages['To'] = receiver_address
            mail_content = """Hello {},\n\tYou have taken responsibility of returning the item "{}" to "{}".""".format(session['userid'], Object, returnedto)
            messages['Subject'] = 'Regarding Returning of an item by you'   
            messages.attach(MIMEText(mail_content, 'plain'))
            text = messages.as_string()
            sess = smtplib.SMTP('smtp.gmail.com', 587) 
            sess.starttls() 
            sess.login(sender_address, sender_pass)
            sess.sendmail(sender_address, receiver_address, text)
            sess.quit()
        elif(found is not None):
            flash("The userid you have entered in returnedto field in acknowledgement is same as yours, still you are responsible for this object", category='error')
        else:
            returnedto=None
            mycursor.execute("update foundobinfo set  description=%s, remarks=%s , updatedby= %s, updatedtime=%s where foundid=%s", ( description, remarks, session['userid'],updatedtime, foundid))
            mydb.commit()
            flash("The userid you have entered in returned to field doesnot exist status not updated still you are responsible for this object", category='error')
    
    else:
        returnedtime=None
        returnedto=None
        if(collectfrom is None):
            mycursor.execute("update foundobinfo set  description=%s, remarks=%s ,   updatedby=%s,  updatedtime=%s where foundid=%s", (description, remarks,  session['userid'],updatedtime, foundid))
        else:
            mycursor.execute("update foundobinfo set  description=%s, remarks=%s , collectfrom = %s, updatedby=%s,  updatedtime=%s where foundid=%s", (description, remarks,  collectfrom, session['userid'],updatedtime, foundid))      
    mydb.commit()
    mycursor.close()
    return redirect(url_for("auth.searchfound"))
    
@auth.route('/searchlost', methods=["GET", "POST"])
def searchlost():
    if 'loggedin' in session:
        mycursor = mydb.cursor()
        Headings = ['Object Name', 'Reported By', 'Lost Date' , 'Status', 'Lost Time', 'Size', 'Brand', 'Color', 'Description', 'Remarks', 'Lost Location', 'Reported time']
        headings=['Object Name', 'Reported By', 'Lost date', 'Status', 'View', 'Update', 'Delete']
        if request.method=='POST':
            searcher=request.form.get('Search')
            searchob=request.form.get('searcher')
            if(searcher == "1"):
                mycursor.execute("select lostid, object, reportedby, lostdate,  objstatus, losttime, size, brand, color, description, remarks, location,  reportedtime from lostobinfo f join locations l on f.locationid=l.locationid where object=%s",(searchob,))
                sdata=mycursor.fetchall()
            elif(searcher == "2"):
                mycursor.execute("select lostid, object, reportedby, lostdate,  objstatus, losttime, size, brand, color, description, remarks, location,  reportedtime from lostobinfo f join locations l on f.locationid=l.locationid where lostdate=%s",(searchob,))
                sdata=mycursor.fetchall()
            elif(searcher== "3"):
                mycursor.execute("select lostid, object, reportedby, lostdate,  objstatus, losttime, size, brand, color, description, remarks,  location, reportedtime from lostobinfo f join locations l on f.locationid=l.locationid where reportedby=%s",(searchob,))
                sdata=mycursor.fetchall()
            else:
                mycursor.execute("select lostid, object, reportedby, lostdate,  objstatus, losttime, size, brand, color, description, remarks,  location, reportedtime from lostobinfo f join locations l on f.locationid=l.locationid where objstatus=%s",(searchob,))
                sdata=mycursor.fetchall()
            
        else:
            mycursor.execute("select lostid, object, reportedby, lostdate,  objstatus, losttime, size, brand, color, description, remarks,  location, reportedtime from lostobinfo f join locations l on f.locationid=l.locationid ")
            sdata = mycursor.fetchall()
        if(sdata):
            return render_template("search lost.html", headings=headings, sdata=sdata, Headings=Headings)
        else:
            flash("No records found matching current search", category='error')
            return render_template("search lost.html", headings=None, sdata=None, Headings=None)
    else:
        flash("You may be logged out/ You may not have logged in yet Please login to enter", category="error")
        return redirect(url_for('auth.login'))
@auth.route('/updatel', methods=['GET', 'POST'])
def updatel():
    Object = request.form.get('Object Name')
    lostid=request.form.get('lostid')
    status = request.form.get('Status')
    description = request.form.get('Description')
    if(description):
        pass
    else:
        description = 'NULL'
    remarks = request.form.get('Remarks')
    if(remarks):
        pass
    else:
        remarks = 'NULL'
    updatedtime=datetime.now()
    mycursor = mydb.cursor()
    if(status):
        mycursor.execute("update lostobinfo set  objstatus = %s, description=%s, remarks=%s , updatedby=%s,  updatedtime=%s where lostid=%s", (status, description, remarks,  session['userid'],updatedtime, lostid))
    else:
        mycursor.execute("update lostobinfo set  description=%s, remarks=%s ,  updatedby=%s,  updatedtime=%s where lostid=%s", (description, remarks, session['userid'],updatedtime, lostid))   
    mydb.commit()
    mycursor.close()
    
    return redirect(url_for("auth.searchlost"))
    
@auth.route('/delete', methods=['GET', 'POST'])
def delete():
    Object = request.form.get('Object Name')
    lostid=request.form.get('lostid')
    mycursor=mydb.cursor()
    mycursor.execute("delete from lostobinfo where object=%s and lostid=%s", (Object, lostid))
    mydb.commit()
    mycursor.close()
    return redirect(url_for("auth.searchlost"))
