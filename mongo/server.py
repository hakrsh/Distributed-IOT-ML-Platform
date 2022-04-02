import pymongo 
from pymongo import MongoClient
from flask import Flask
from flask import request, render_template, url_for
app = Flask(__name__)

client = MongoClient('mongodb+srv://root:root@ias.tu9ec.mongodb.net/')
db = client.users
collection = db.tryusers
# cid = collection.insert_one({'username': username,'roles':['ai-dev','app-dev'],'password':'1234'})

# @app.route('/users/signup', methods=['GET','POST'])
@app.route('/')
def signup():
    if request.method == 'GET': 
        return render_template('index.html')
    elif request.method == 'POST':
        # req = request['data']
        # username, role, passwd = req.username, req.role, req.passwd
        username = 'user1'
        role='temp'
        passwd= '1234'
        collection = db[role]
        cid = collection.insert_one({'username': username,'password':passwd})
        tmp = collection.find_one({'username':username})
        print(tmp)
        cid = collection.insert_one({'username': username,'password':passwd})
        print(cid)
        return 'Success'

@app.route('/users/login', methods=['GET','POST'])
def login():
    pass
@app.route('/users/logout',  methods=['GET' ,'POST'])
def logout():
    pass
# cid = collection.insert_one({'username':'user2','role':'app-dev','email':'user1@gmail.com','password':'1234'})

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=2500)
