import smtplib, random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, redirect,url_for,render_template,session, request, flash
from datetime import datetime
from DataBaseTable import *
from settings import app,db
session_register = {}

@app.route("/", methods = ['POST','GET'])
def login():
    session_register = {}
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        session_username = UserInfo.query.filter_by(username = email).first()
        session_password = UserInfo.query.filter_by(password = password).first()

        if session_username and session_password:
            return redirect(url_for('user'))
        else:
            flash(' Your account is not registered yet.')
            return redirect(url_for('login'))

    return render_template("base.html")

@app.route("/register", methods = ['POST','GET'])
def register():
    if request.method == 'POST':
        session_register['name'] = request.form['name']
        session_register['email'] = request.form['email'] 
        session_register['password'] = request.form['password']
        session_register['repeat-password'] = request.form['repeat-password']

        email_exist = UserInfo.query.filter_by(username=session_register['email']).first()
    
        if ( session_register['name'] and
            session_register['email'] and 
            session_register['password'] and 
            session_register['repeat-password'] ):
            if email_exist:
                flash(' Email is already taken, please use another email.')
                return redirect(url_for('register'))
            elif session_register['password'] != session_register['repeat-password']:
                flash(' Password repeatition is not validated.')
                return redirect(url_for('register'))
            else:
                return redirect(url_for('otp'))
        else:
            flash(' You should check in on some of those fields above.')
            return redirect(url_for('register'))

    return render_template("register.html")

@app.route("/user")
def user():
    return f'LOG IN SUCESSFUL'

@app.route('/verify_otp', methods=['POST','GET'])
def verify_otp():
    data = request.get_json()
    
    if session_register['otp'] == data['pin_data']:
        Add_User = UserInfo(session_register['name'],session_register['email'],session_register['password'])
        db.session.add(Add_User)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        return redirect(url_for('register')) 

@app.route("/otp", methods = ['POST','GET'])
def otp():

    generated_otp = ''
    for i in range(4):
        generated_otp += str(random.randint(0,9))

    session_register['otp'] = generated_otp
    mail_content = f"YOU'RE OTP PIN IS: {generated_otp}"
    #The mail addresses and password
    sender_address = 'otpsender47@gmail.com'
    sender_pass = 'xisnpznnkhkhcbls'
    receiver_address = session_register['email']
    
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'ONE TIME PIN REGISTRATION.'   #The subject line
    
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
   
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')

    return render_template('verification.html', email=session_register['email'])

if __name__ == "__main__":
    app.run(debug=True)