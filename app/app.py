import random
from flask import Flask, render_template, request, url_for, redirect, session
import pymongo
import bcrypt
import pickle

app = Flask(__name__)


app.secret_key = "testing"

# client = pymongo.MongoClient("mongodb+srv://root:root@ias.tu9ec.mongodb.net/hospital?retryWrites=true&w=majority")
client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client.get_database('hospital')

records = db.register
patients = db.patient
doctors = db.doctor


@app.route("/", methods=['post', 'get'])
def index():
    message = ''
    
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
         
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        
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
            
            user_input = {'name': user, 'email': email, 'password': hashed}
            
            records.insert_one(user_input)
            
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
            
            return render_template('logged_in.html', email=new_email)
    return render_template('index.html')



@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            #encode the password and check if it matches
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
            if(patients.count_documents({}) < 1):
                patient_name = request.form.get("fullname")
                disease_type = request.form.get("disease")
                patient_input = {'name': patient_name, 'disease': disease_type}
                
                patients.insert_one(patient_input)
            
                patient_found = patients.find_one({"name": patient_name})
                if patient_found:
                    return redirect(url_for("add_doctor"))
    else:
        return redirect(url_for("login"))
     
    return render_template('add_patient.html')

@app.route("/delete_patient", methods=["POST", "GET"])
def delete_patient():
    if "email" in session:
        db.patient.drop()
        db.doctor.drop()
    else:
        return redirect(url_for("login"))
    return redirect(url_for("add_patient"))


@app.route("/add_doctor", methods=["POST", "GET"])
def add_doctor():
    if "email" in session:
        if request.method == "POST":
            doctor_name = request.form.get("fullname")
            doctor_phone_number = request.form.get("phonenumber")
            doctor_input = {'name': doctor_name, 'phone_number': doctor_phone_number}
            doctors.insert_one(doctor_input)
    else:
        return redirect(url_for("login"))
    return render_template('add_doctor.html')


@app.route("/show_patient", methods=["POST", "GET"])
def show_patient():

    data1 = ""
    data2 = ""
    data3 = ""
    data4 = ""

    if "email" in session:
        if(patients.count_documents({}) != 0):
            patient_name = patients.find()[0]['name']
            patient_disease = patients.find()[0]['disease']

            data1 += patient_name + " : "
            data1 += patient_disease

            n = doctors.count_documents({})
            for i in range(n):
                doctor_name = doctors.find()[i]['name']
                doctor_phone_number = doctors.find()[i]['phone_number']
                data2 += doctor_name + " : "
                data2 += doctor_phone_number
                data2 += " "
            spo2 = random.randint(60, 100)
            temperature = random.randint(97, 105)
            pulse = random.randint(40, 100)
            row = [spo2, temperature, pulse]
            file = open('model.pkl', 'rb')     
            model = pickle.load(file)
            result = model.predict([row])[0]

            data3+= "SPO2: " + str(row[0]) + ", " + "Temperature: " + str(row[1]) + ", " + "Pulse Rate: " + str(row[2])
                #data3 += str(j) + " "
    
            if(result == 1):
                data4 = "Critical"
            else:
                data4 = "Safe"
            
        
        else:
            data1 = "No patients in database"

    else:
        return redirect(url_for("login"))
    
        
    return render_template('show_patient.html', patient_data = data1, doctor_data = data2, sensor_data = data3, patient_condition = data4)



if __name__ == "__main__":
  app.run(port=8000, debug=True)
