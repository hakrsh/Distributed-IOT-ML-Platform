from flask import request, render_template, redirect
from auth import app, db, module_config

# client = MongoClient('mongodb+srv://root:root@ias.tu9ec.mongodb.net/')
# db = client.users

@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'GET': 
        return render_template('index.html')
    elif request.method == 'POST':
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
            return redirect('/users/login')
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
        if cid is None: # invalid
            response['status'] = 500
            return render_template('login.html', response=response)
        if role == 'ai-dev':
            # response['ip'] = module_config['model_dash']
            return render_template('model-dash.html', response=response,url=module_config['platform_api'])
        elif role == 'app-dev':
            return render_template('application-dash.html', response=response,url=module_config['platform_api'])
        elif role == 'plt-mngr':
            return render_template('application-dash.html', response=response,url=module_config['platform_api'])
        elif role == 'snsr-mngr':
            return render_template('sensor-dash.html', response=response,url=module_config['sensor_api'])
        elif role == 'scheduler':
            return render_template('scheduler-dash.html', response=response,url=module_config['scheduler'])

        return render_template('index.html', response=response)

def start():
    app.run(host='0.0.0.0', port=2500)
