import pymongo 
from pymongo import MongoClient
from flask import Flask
from flask import request, render_template, url_for
app = Flask(__name__)

client = MongoClient('mongodb+srv://root:root@ias.tu9ec.mongodb.net/')
db = client.users

# @app.route('/', methods=['GET','POST'])
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/users/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET': 
        return render_template('signup.html')
    elif request.method == 'POST':
        req = request.form
        username, role, passwd = req.get('username'), req.get('role'), req.get('password')
        collection = db[role]
        cid = collection.find_one({'username':username, 'password':passwd})
        response = {}
        response['user'] = username
        response['password'] = passwd
        response['role'] = role
        response['action'] = 'signup'
        if cid is None:
            cid = collection.insert_one({'username': username,'password':passwd})
            response['status'] = 200
        else:
            response['status'] = 500
        return render_template('index.html', response = response)

@app.route('/users/login', methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == 'POST':
        req = request.form
        username, role, passwd = req.get('username'), req.get('role'), req.get('password')
        collection = db[role]
        cid = collection.find_one({'username':username, 'password':passwd})
        response = {}
        response['user'] = username
        response['password'] = passwd
        response['role'] = role
        response['status'] = 200
        response['action'] = 'login'
        if cid is None:
            response['status'] = 500
        return render_template('index.html', response = response)

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=2500)
