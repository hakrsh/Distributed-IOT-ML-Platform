import json
import subprocess
import threading
import time
from flask import request, render_template, jsonify
import requests
import uuid
from platform_manager import app, db, module_config, fs
import logging
import zipfile
import os
import shutil
import os
import httpx
from jsonschema import validate
import importlib.resources as pkg_resources
from platform_manager import messenger

logging.basicConfig(level=logging.INFO)

def clear(path):
    os.remove(path + '.zip')
    shutil.rmtree(path)
    logging.info('Temp files removed')


@app.route('/')
def index():
    return 'Platform manager running!'


@app.route('/upload-model', methods=['GET', 'POST'])
def upload_model():
    if request.method == 'GET':
        return render_template('upload_model.html')
    elif request.method == 'POST':
        model_name = request.form['model_name']
        if db.models.find_one({'ModelName': model_name}) is not None:
            return 'Model already exists'
        ModelId = str(uuid.uuid4())[:8]
        logging.info('ModelId: ' + ModelId)
        content = request.files['model_zip'].read()
        model_contract = json.loads(request.files['model_contract'].read())
        model_contract_schema = json.loads(pkg_resources.read_binary('platform_manager', 'model_contract_schema.json'))
        try:
            validate(instance=model_contract, schema=model_contract_schema)
        except Exception as e:
            return 'Model contract validation failed: '
        logging.info('Model contract validation passed')
        with open('/tmp/' + ModelId + '.zip', 'wb') as f:
            f.write(content)
        logging.info('Model saved to /tmp/' + ModelId + '.zip')
        with zipfile.ZipFile('/tmp/' + ModelId + '.zip', 'r') as zip_ref:
            zip_ref.extractall('/tmp/' + ModelId)
        logging.info('Model extracted to /tmp/' + ModelId)
        logging.info('Validating model zip...')
        if not os.path.exists(f'/tmp/{ModelId}/{model_contract["root_dir"]}'):
            return 'Model zip is invalid'
        if not os.path.exists(f'/tmp/{ModelId}/{model_contract["requirements"]}'):
            return 'Model requirements not found'
        if not os.path.exists(f'/tmp/{ModelId}/{model_contract["readme"]}'):
            return 'Model readme not found'
        logging.info('Model validation passed...')
        readme = open(f'/tmp/{ModelId}/{model_contract["readme"]}', 'r').read()
        logging.info('Uploading model...')
        file = fs.put(content, filename=ModelId+'.zip')
        db.models.insert_one({"ModelId": ModelId, "ModelName": model_name,
                              "content": file, "readme":readme, "contract": model_contract})
        logging.info('Model uploaded successfully')
        clear('/tmp/' + ModelId)
        messenger.send_message('to_deployer_master', {"type":"model","ModelId": ModelId, "model_name": model_name})
        logging.info('Model deployment request has been written to kafka topic to_deployer_master')
        return 'Model uploaded successfully'

app_contract = None
ApplicationID = None

@app.route('/get-running-models', methods=['GET'])
def get_running_models():
    global app_contract
    if app_contract is None:
        return 'Secret key not set'
    instances = db.instances.find()
    data = []
    for instance in instances:
        if instance['type'] == 'model' and instance['status'] == 'running':
            logging.info('Model: ' + instance['model_id'])
            model_contract = db.models.find_one({'ModelId': instance['model_id']})['contract']
            if model_contract['secret_key'] == app_contract['secret_key']:
                for function in model_contract['functions']:
                    model_name = instance['model_name'] + '/' + function['api_endpoint']    
                    model_id = instance['model_id'] + '/' + function['api_endpoint']
                    data.append({'model_id': model_id, 'model_name': model_name})
    return json.dumps(data)

@app.route('/upload-app', methods=['POST', 'GET'])
def upload_app():
    global app_contract
    global ApplicationID
    if request.method == 'GET':
        return render_template('upload_app_contract.html')
    if request.method == 'POST':
        ApplicationID = str(uuid.uuid4())[:8]
        ApplicationName = request.form.get('ApplicationName')
        if db.applications.find_one({"ApplicationName": ApplicationName}):
            return 'Application already exists'
        content = request.files['app_zip'].read()
        app_contract = json.loads(request.files['app_contract'].read())
        app_contract_schema = json.loads(pkg_resources.read_binary('platform_manager', 'app_contract_schema.json'))
        try:
            validate(instance=app_contract, schema=app_contract_schema)
        except Exception as e:
            return 'Application contract validation failed: '
        logging.info('Application contract validation passed')
        with open('/tmp/' + ApplicationID + '.zip', 'wb') as f:
            f.write(content)
        logging.info('Application saved to /tmp/' + ApplicationID + '.zip')
        with zipfile.ZipFile('/tmp/' + ApplicationID + '.zip', 'r') as zip_ref:
            zip_ref.extractall('/tmp/' + ApplicationID)
        logging.info('Application extracted to /tmp/' + ApplicationID)
        logging.info('Validating application zip...')
        if not os.path.exists(f'/tmp/{ApplicationID}/{app_contract["root_dir"]}'):
            return 'Application zip is invalid'
        if not os.path.exists(f'/tmp/{ApplicationID}/{app_contract["requirements"]}'):
            return 'Application requirements not found'
        logging.info('Application zip validation passed...')
        logging.info('Uploading application...')
        file = ''
        with open('/tmp/' + ApplicationID + '.zip', 'rb') as f:
            file = fs.put(f, filename=ApplicationID + '.zip')
        db.applications.insert_one(
            {"ApplicationID": ApplicationID, "ApplicationName": ApplicationName, "app_contract": app_contract, "content": file})
        logging.info('Application uploaded successfully')
        clear('/tmp/' + ApplicationID)
        running_models = json.loads(get_running_models())
        return render_template('choose_models.html', models=running_models, app_contract=app_contract)
        

@app.route('/choose-models',methods=['GET','POST'])
def choose_models():
    global app_contract
    if request.method == 'POST':
        logging.info('Binding models to application...')
        model_bindings = []
        i = 1
        while True:
            if request.form.get('model' + str(i) + '_name') is None:
                break
            model_bindings.append({
                'model_id': request.form.get('model' + str(i) + '_id'),
                'model_name': request.form.get('model' + str(i) + '_name')
            })
            i += 1
        models = {}
        for model in model_bindings:
            models[model['model_name']] = module_config['model_req_handler'] + '/' + model['model_id']
        app_contract['models'] = models
        logging.info('Updating application contract...')
        db.applications.update_one({'ApplicationID': ApplicationID},{'$set': {'app_contract': app_contract}})
        logging.info('Application contract updated successfully')
        return 'Application uploaded successfully'
           
@app.route('/api/get-applications', methods=['GET'])
def fetch_applications():
    applications = db.applications.find()
    data = []
    for application in applications:
        temp = {}
        temp['ApplicationID'] = application['ApplicationID']
        temp['ApplicationName'] = application['ApplicationName']
        temp['Contract'] = application['app_contract']
        data.append(temp)
    return json.dumps(data)


@app.route('/api/get-application/<ApplicationID>', methods=['GET'])
def fetch_application(ApplicationID):
    application = db.applications.find_one({"ApplicationID": ApplicationID})
    data = {'ApplicationID': application['ApplicationID'],
            'ApplicationName': application['ApplicationName'], 'Contract': application['app_contract']}
    return json.dumps(data)

def render_readme(body):
    response = httpx.post(
        "https://api.github.com/markdown",
        json={
            "mode": "markdown",
            "text": body,
        })

    if response.status_code == 200:
        return response.text
    else:
        return "Error"

@app.route('/view-readme/<model_id>', methods=['GET'])
def view_readme(model_id):
    logging.info('Fetching readme for model: ' + model_id)
    model = db.models.find_one({"ModelId": model_id})
    if model is None:
        return 'Model not found'
    if model['readme'] is None:
        return 'No readme found'
    return render_readme(model['readme'])

@app.route('/view-contract/<type>/<id>', methods=['GET'])
def view_contract(type, id):
    logging.info('Fetching contract for : ' + type + ' ' + id)
    if type == 'model':
        model = db.models.find_one({"ModelId": id})
        if model is None:
            return 'Model not found'
        if model['contract'] is None:
            return 'No contract found'
        data = model['contract']
    elif type == 'app':
        application = db.applications.find_one({"ApplicationID": id})
        if application is None:
            return 'Application not found'
        if application['app_contract'] is None:
            return 'No contract found'
        data = application['app_contract']
    response = app.response_class(
        response=json.dumps(data, indent=4),
        mimetype='application/json'
    )
    return response

@app.route('/get-model-dashboard', methods=['GET'])
def get_model_dashboard():
    instances = db.instances.find()
    data = []
    for instance in instances:
        if instance['type'] == 'model':
            logging.info('Model: ' + instance['model_id'])
            data.append({'model_id': instance['model_id'], 'model_name': instance['model_name'],
                         'status': instance['status'], 'ip': instance['ip'],
                         'port': instance['port'], 'host': instance['hostname'],
                         'url': f'{module_config["platform_api"]}/view-readme/' + instance['model_id'],
                         'contract': f'{module_config["platform_api"]}/view-contract/model/' + instance['model_id']})
    return render_template('model_dashboard.html', data=data)

@app.route('/get-running-applications', methods=['GET'])
def get_running_applications():
    instances = db.instances.find()
    data = []
    for instance in instances:
        if instance['type'] == 'app':
            logging.info('Instance: ' + instance['instance_id'])
            url = "http://" + instance['ip'] + ':' + str(instance['port'])
            data.append({'instance_id': instance['instance_id'],
                        'hostname': instance['hostname'], 'ip': instance['ip'], 'port': instance['port'],
                         'url': url, 'app_name': instance['app_name'], 'status': instance['status'],
                         'contract': f'{module_config["platform_api"]}/view-contract/app/' + instance['application_id']})
    return render_template("app_dashboard.html", data=data)


def execute(cmd):
    subprocess.call(cmd, shell=True)


@app.route('/create-new-vm', methods=['GET'])
def create_vm():
    cmd = 'bash ./platform_manager/dynamic_scaling.sh'
    threading.Thread(target=execute, args=(cmd,)).start()
    return 'VM creation on progress...'

def worker_status_update():
    while True:
        workers = db.workers
        for worker in json.loads(pkg_resources.read_binary('platform_manager', 'config.json'))['workers']:
            try:
                if requests.get(f'http://{worker["ip"]}:9898').status_code == 200:
                    time.sleep(5)
                    if workers.find_one({"ip": worker["ip"]}) is None:
                        db.workers.insert_one({"ip": worker["ip"], "name": worker["name"], "status": "up"})
                    else:
                        db.workers.update_one({"ip": worker["ip"]}, {"$set": {"status": "up"}})
            except:
                if workers.find_one({"ip": worker["ip"]}) is None:
                        db.workers.insert_one({"ip": worker["ip"], "name": worker["name"], "status": "down"})
                else:
                    db.workers.update_one({"ip": worker["ip"]}, {"$set": {"status": "down"}})
        time.sleep(10)

@app.route('/get-workers-status', methods=['GET'])
def get_workers_status():
    workers = db.workers.find()
    data = []
    for worker in workers:
        data.append({'ip': worker['ip'], 'name': worker['name'], 'status': worker['status']})
    return render_template('workers_status.html', workers=data)

def start():
    app.run(host='0.0.0.0', port=5000)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/get-load')
def home():
    """
        Fetches the application and models load data from all the virtual VMs
    """
    url = module_config['deployer_master']
    print(url)
    print((f'{url}get-load'))
    response = requests.get(f'{url}get-load')
    load_url = url+"get-load"
    print(load_url)
    load_data = json.loads(response.content.decode('utf-8'))

    print(type(load_data))

    return render_template("load-data.html", load_data=load_data, url=load_url)


@app.route('/get-load-json')
def get_load_json():
    """
        Fetches the application and models load data from all the virtual VMs
    """
    url = module_config['deployer_master']
    print(url)
    print((f'{url}get-load'))
    response = requests.get(f'{url}get-load')
    load_url = url+"get-load"
    print(load_url)
    load_data = jsonify(json.loads(response.content.decode('utf-8')))

    return load_data
