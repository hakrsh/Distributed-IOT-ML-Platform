import pymongo 
from pymongo import MongoClient
from flask import Flask
from flask import request, render_template, url_for
app = Flask(__name__)

client = MongoClient('mongodb+srv://root:root@ias.tu9ec.mongodb.net/')
db = client.users

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/users/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET': 
        return render_template('signup.html')
    elif request.method == 'POST':
        req = request.get_data()
        username, role, passwd = req.username, req.role, req.passwd
        # username = 'user1'
        # role='scheduler'
        # passwd= '1234'
        collection = db[role]
        tmp = collection.find_one({'username':username, 'password':passwd})
        if tmp == None:
            return 'Invalid'
        cid = collection.insert_one({'username': username,'password':passwd})
        print(cid)
        return 'Success'

@app.route('/users/login', methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == 'POST':
        req = request.get_data()
        username, role, passwd = req.username, req.role, req.passwd
        collection = db[role]
        tmp = collection.find_one({'username':username, 'password':passwd})
        if tmp == None:
            return 'Invalid'
        return 'Success'

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=2500)
