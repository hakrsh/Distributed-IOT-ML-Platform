from flask import flash, request, render_template, redirect
from auth import app, db, module_config

app.secret_key = 'super secret key'

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        return render_template('login.html')


@app.route('/users/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        req = request.form
        username, role, passwd,passwd_repeat = req.get(
            'username'), req.get('role'), req.get('password'), req.get('password_repeat')
        # if passwd != passwd_repeat:
        #     flash('Passwords do not match', 'error')
        #     return render_template('signup.html')
        collection = db[role]
        if collection.find_one({'username': username}):
            flash('Username already exists', 'error')
            return render_template('signup.html')
        else:
            response = {}
            response['user'] = username
            response['password'] = passwd
            response['role'] = role
            response['action'] = 'signup'
            collection.insert_one(
                {'username': username, 'password': passwd})
            response['status'] = 200
            flash('User created successfully!', 'success')
            return redirect('/users/login')



@app.route('/users/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == 'POST':
        req = request.form
        username, role, passwd = req.get(
            'username'), req.get('role'), req.get('password')
        collection = db[role]
        if collection.find_one({'username' : username}) is None:
            flash('User not authorized', 'danger')
            return redirect('/users/login')
        elif collection.find_one({'username' : username, 'password' : passwd}) is None:
            flash('Wrong password', 'danger')
            return redirect('/users/login')
        else:
            flash('User authorized', 'success')
            response = {}
            response['user'] = username
            response['password'] = passwd
            response['role'] = role
            response['status'] = 200
            response['action'] = 'login'
            if role == 'ai_dev':
                # response['ip'] = module_config['model_dash']
                return render_template('model-dash.html', response=response, url=module_config['platform_api'])
            elif role == 'app_dev':
                return render_template('application-dash.html', response=response, url=module_config['platform_api'])
            elif role == 'plt_mngr':
                return render_template('application-dash.html', response=response, url=module_config['platform_api'])
            elif role == 'snsr_mngr':
                return render_template('sensor-dash.html', response=response, url=module_config['sensor_reg_api'])
            elif role == 'scheduler':
                return render_template('scheduler-dash.html', response=response, url=module_config['scheduler'])

def start():
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=2500)
