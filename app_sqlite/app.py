from flask import Flask, render_template, request, url_for, redirect, session
import sqlite3
import pymongo
import bcrypt
import pickle
import json
from time import time
import random

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret key'

conn = sqlite3.connect('database.db')

conn.execute("DROP TABLE IF EXISTS register")
conn.execute("CREATE TABLE register (name TEXT, email TEXT, password TEXT NOT NULL)")

conn.execute("DROP TABLE IF EXISTS patient")
conn.execute("CREATE TABLE patient (name TEXT NOT NULL, disease TEXT NOT NULL)")

conn.execute("DROP TABLE IF EXISTS doctor")
conn.execute("CREATE TABLE doctor (name TEXT NOT NULL, phone TEXT INTEGER)")

conn.close()


def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn


@app.route("/", methods=['post', 'get'])
def index():

    conn = get_db_connection()
    curr = conn.cursor()

    message = ''
    
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        curr.execute('SELECT * FROM register')
        entry = curr.fetchall()
        user_found = False
        email_found = False
        for i in range(len(entry)):
            if user == entry[i][0]:
                user_found = True
                break
        for i in range(len(entry)):
            if email == entry[i][1]:
                email_found = True
                break
   
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())

            curr.execute('INSERT INTO register (name, email, password) VALUES(?, ?, ?)', (user, email, hashed))
            conn.commit()

            curr.execute('SELECT * FROM register')
            new_email = curr.fetchall()
            new_email = new_email[0][1]
            conn.close()
        
            return render_template('logged_in.html', email=new_email)
    return render_template('index.html')



@app.route("/login", methods=["POST", "GET"])
def login():

    conn = get_db_connection()
    curr = conn.cursor()

    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #check if email exists in database
       
        curr.execute('SELECT * FROM register')
        entry = curr.fetchall()
        email_found = False
        for i in range(len(entry)):
            if email == entry[i][1]:
                email_found = True
                break

        conn.close()

        if email_found:
            email_val = entry[i][1]
            passwordcheck = entry[i][2]
            
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    
    return render_template('login.html', message=message)

@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')

@app.route("/add_patient", methods=["POST", "GET"])
def add_patient():

    if "email" in session:
        if request.method == "POST":

            conn = get_db_connection()
            curr = conn.cursor()

            curr.execute('SELECT * FROM patient')
            entry = curr.fetchall()

            if(len(entry) < 1):
                patient_name = request.form.get("fullname")
                disease_type = request.form.get("disease")

                curr.execute('INSERT INTO patient (name, disease) VALUES(?, ?)', (patient_name, disease_type))
                conn.commit()
                conn.close()

                '''curr.execute('SELECT * FROM patient')
                entry = curr.fetchall()'''


                '''patient_found = False

                for i in range(len(entry)):
                    if patient_name == entry[i][0]:
                        patient_found = True
                        break
                if patient_found:'''
                return redirect(url_for("add_doctor"))
            else:
                return redirect(url_for("patient_error"))

                
    else:
        return redirect(url_for("login"))
     
    return render_template('add_patient.html')

@app.route("/delete_patient", methods=["POST", "GET"])
def delete_patient():
    if "email" in session:
        conn = get_db_connection()
        curr = conn.cursor()        
        curr.execute("DELETE FROM patient")
        curr.execute("DELETE FROM doctor")
        conn.commit()
        conn.close()
    else:
        return redirect(url_for("login"))
    return redirect(url_for("add_patient"))


@app.route("/add_doctor", methods=["POST", "GET"])
def add_doctor():

    if "email" in session:
        if request.method == "POST":
            doctor_name = request.form.get("fullname")
            doctor_phone_number = request.form.get("phonenumber")

            conn = get_db_connection()
            curr = conn.cursor()

            curr.execute('INSERT INTO doctor (name, phone) VALUES(?, ?)', (doctor_name, doctor_phone_number))
            conn.commit()
            conn.close()
    else:
        return redirect(url_for("login"))

    return render_template('add_doctor.html')


@app.route("/show_patient", methods=["POST", "GET"])
def show_patient():

    if "email" in session:
        print("OK")
    else:
        return redirect(url_for("login"))
        
    return render_template('show_patient.html')

@app.route("/live-data-new", methods=["POST", "GET"])
def live_data_new():
    data1 = ""
    data2 = ""
    data3 = ""
    data4 = ""

    # API Calls here
    spo2 = random.randint(60, 100)
    temperature = random.randint(97, 105)
    pulse = random.randint(40, 100)
    
    row = [spo2, temperature, pulse]
    
    # open pkl file
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    result = model.predict([row])[0]

    if(result == 1):
        data4 = "Critical"
    else:
        data4 = "Safe"


    data = {}
    data['spo2'] = spo2
    data['temperature'] = temperature
    data['pulse'] = pulse
    data['condition'] = data4
    data['timestamp'] = time() * 1000

    conn = get_db_connection()
    curr = conn.cursor()

    curr.execute('SELECT * FROM patient')
    entry = curr.fetchall()

    if(len(entry) > 0):
        patient_name = entry[0][0]
        patient_disease = entry[0][1]
        patient_data = ""
        patient_data += patient_name + " : "
        patient_data += patient_disease
    else:
        patient_data = "No patient data"

    data['patient_data'] = patient_data

    doc_data = ""
    curr.execute('SELECT * FROM doctor')
    entry = curr.fetchall()
    n = len(entry)
    for i in range(n):
        doctor_name = entry[i][0]
        doctor_phone_number = entry[i][1]
        doc_data += doctor_name + " - "
        doc_data += doctor_phone_number
        doc_data += " "

    data['doctor_data'] = doc_data

    print(data)
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    conn.close()
    return response

@app.route("/patient_error", methods=["POST", "GET"])
def patient_error():
    return render_template('patient_error.html')
    

if __name__ == "__main__":
  app.run(port=8000, debug=True)
