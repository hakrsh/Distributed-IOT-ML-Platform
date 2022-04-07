import json
from pyexpat import model
from flask import request, render_template, jsonify
import requests
import uuid
from platform_manager import app, db, module_config, fs
import logging
import zipfile
import os
import shutil
from jsonschema import validate

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
        ModelId = str(uuid.uuid4())
        logging.info('ModelId: ' + ModelId)
        content = request.files['file'].read()
        with open('/tmp/' + ModelId + '.zip', 'wb') as f:
            f.write(content)
        logging.info('Model saved to /tmp/' + ModelId + '.zip')
        with zipfile.ZipFile('/tmp/' + ModelId + '.zip', 'r') as zip_ref:
            zip_ref.extractall('/tmp/' + ModelId)
        logging.info('Model extracted to /tmp/' + ModelId)
        logging.info('Validating model...')
        if not os.path.exists('/tmp/' + ModelId + '/model/requirements.txt'):
            clear('/tmp/' + ModelId)
            return 'requirements.txt not found'
        if not os.path.exists('/tmp/' + ModelId + '/model/model.pkl') and not os.path.exists('/tmp/' + ModelId + '/model/model.h5'):
            clear('/tmp/' + ModelId)
            return 'model.pkl or model.h5 not found'
        if not os.path.exists('/tmp/' + ModelId + '/model/model_contract.json'):
            clear('/tmp/' + ModelId)
            return 'model_contract.json not found'
        if not os.path.exists('/tmp/' + ModelId + '/model/preprocessing.py'):
            clear('/tmp/' + ModelId)
            return 'preprocessing.py not found'
        if not os.path.exists('/tmp/' + ModelId + '/model/postprocessing.py'):
            clear('/tmp/' + ModelId)
            return 'postprocessing.py not found'
        logging.info('Validating model_contract.json...')
        schema = {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "endpoint": {
                    "type": "string"
                }
            },
            "required": ["name", "endpoint"]
        }
        model_contract = {}
        with open('/tmp/' + ModelId + '/model/model_contract.json', 'r') as f:
            model_contract = json.load(f)
        try:
            validate(model_contract, schema)
        except :
            clear('/tmp/' + ModelId)
            return 'model_contract.json is not valid'
        logging.info('Model validation passed...')
        logging.info('Uploading model...')
        file = fs.put(content, filename=ModelId+'.zip')
        db.models.insert_one({"ModelId": ModelId, "ModelName": model_name,
                              "model_contract": model_contract, "content": file})
        logging.info('Model uploaded successfully')
        clear('/tmp/' + ModelId)
        url = module_config['deployer_master'] + '/model'
        logging.info('Sending model to deployer')

        response = requests.post(url, json={"ModelId": ModelId,"model_name":model_name}).content

        return response.decode('ascii')


@app.route('/get-model/<ModelId>', methods=['GET'])
def get_model(ModelId):
    logging.info('ModelId: ' + ModelId)
    model = db.models.find_one({"ModelId": ModelId})
    return {'ModelId': model['ModelId'], 'ModelName': model['ModelName'], 'model_contract': model['model_contract']}


@app.route('/get-models', methods=['GET'])
def get_models():
    models = db.models.find()
    data = []
    for model in models:
        data.append({'ModelId': model['ModelId'], 'ModelName': model['ModelName'],
                    'model_contract': model['model_contract']})
    return json.dumps(data)


@app.route('/get-running-model-config', methods=['GET'])
def get_running_model_config():
    model_id = request.json['model_id']
    instance_id = request.json['instance_id']
    model = get_model(model_id)
    instace = db.instances.find_one({"instance_id": instance_id})
    model_contract = model['model_contract']
    model_contract['ip'] = instace['ip']
    model_contract['port'] = instace['port']
    return model_contract

@app.route('/get-running-models', methods=['GET'])
def get_running_models():
    instances = db.instances.find()
    data = []
    for instance in instances:
        if instance['type'] == 'model':
            logging.info('Instance: ' + instance['instance_id'])
            logging.info('Model: ' + instance['model_id'])
            model = get_model(instance['model_id'])
            if model is not None:
                data.append({'instance_id': instance['instance_id'],
                            'model_id': instance['model_id'], 'ModelName': model['ModelName']})
    return json.dumps(data)

@app.route('/get-model-dashboard', methods=['GET'])
def get_model_dashboard():
    instances = db.instances.find()
    data = []
    for instance in instances:
        if instance['type'] == 'model':
            print(instance)
            logging.info('Instance: ' + instance['instance_id'])
            logging.info('Model: ' + instance['model_id'])
            model = get_model(instance['model_id'])
            data.append({'ModelName': model['ModelName'],
                        'ip': instance['ip'], 'port': instance['port'],
                        'host': instance['hostname']})
    return render_template("model_dashboard.html", data = data)


@app.route('/get-running-applications', methods=['GET'])
def get_running_applications():
    instances = db.instances.find()
    print(instances)
    data = []
    for instance in instances:
        if instance['type'] == 'app':
            logging.info('Instance: ' + instance['instance_id'])
            url = "http://" + instance['ip'] + ':' + str(instance['port'])
            data.append({'instance_id': instance['instance_id'],
                        'hostname': instance['hostname'], 'ip': instance['ip'], 'port': instance['port'],
                        'url': url, 'app_name': instance['app_name'], 'status': instance['status']  })
    return render_template ("app_dashboard.html", data = data)

@app.route('/upload-app', methods=['POST', 'GET'])
def upload_app():
    if request.method == 'GET':
        running_models = json.loads(get_running_models())
        return render_template('upload_app.html',models=running_models)
    if request.method == 'POST':
        data = request.form
        ApplicationID = str(uuid.uuid4())
        ApplicationName = data['ApplicationName']
        if db.applications.find_one({"ApplicationId": ApplicationID}):
            return 'Application already exists'
        content = request.files['file'].read()
        with open('/tmp/' + ApplicationID + '.zip', 'wb') as f:
            f.write(content)
        logging.info('Application saved to /tmp/' + ApplicationID + '.zip')
        with zipfile.ZipFile('/tmp/' + ApplicationID + '.zip', 'r') as zip_ref:
            zip_ref.extractall('/tmp/' + ApplicationID)
        logging.info('Application extracted to /tmp/' + ApplicationID)
        logging.info('Validating application...')
        if not os.path.exists('/tmp/' + ApplicationID + '/app/app_contract.json'):
            clear('/tmp/' + ApplicationID)
            return 'app_contract.json not found'
        if not os.path.exists('/tmp/' + ApplicationID + '/app/src'):
            clear('/tmp/' + ApplicationID)
            return 'src directory not found'
        if not os.path.exists('/tmp/' + ApplicationID + '/app/requirements.txt'):
            clear('/tmp/' + ApplicationID)
            return 'requirements.txt not found'
        logging.info('Validating app_contract.json...')
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "sensors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "function": {"type": "string"},
                            "sensor_type": {"type": "string"}
                        },
                        "required": ["function", "sensor_type"]
                    },
                    "minItems": 1,
                    "uniqueItems": True,
                },
            },
            "required": ["name", "sensors"]
        }
        app_contract = {}
        with open('/tmp/' + ApplicationID + '/app/app_contract.json', 'r') as f:
            app_contract = json.load(f)
        try:
            validate(app_contract, schema)
        except:
            clear('/tmp/' + ApplicationID)
            return 'app_contract.json is not valid'
        logging.info('Validations passed')
        
        model_instance_id = request.form['model_instance_id']
        logging.info('Model instance id: ' + model_instance_id)
        model_id = db.instances.find_one({"instance_id": model_instance_id})['model_id']
        logging.info('model_id: ' + model_id)
        model_config = requests.get('http://localhost:5000/get-running-model-config',json={"model_id": model_id, "instance_id": model_instance_id}).json()
        with open('/tmp/' + ApplicationID + '/app/model_contract.json', 'w') as f:
            json.dump(model_config, f)
        logging.info('Inserted model contract into app')
        shutil.make_archive('/tmp/' + ApplicationID,
                            'zip', '/tmp/' + ApplicationID)
        logging.info('Uploading application...')
        file = ''
        with open('/tmp/' + ApplicationID + '.zip', 'rb') as f:
            file = fs.put(f,filename=ApplicationID + '.zip')
        db.applications.insert_one(
            {"ApplicationID": ApplicationID, "ApplicationName": ApplicationName, "app_contract": app_contract, "content": file})
        logging.info('Application uploaded successfully')
        clear('/tmp/' + ApplicationID)
        return 'Application stored successfully'


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



@app.route('/get-load')
def home():
    """
        Fetches the application and models load data from all the virtual VMs
    """
    url = module_config['deployer_master']
    response = requests.get(f'{url}get-load')
    load_url = url+"get-load"
    load_data = json.loads(response.content.decode('utf-8'))
    return render_template ("load-data.html", load_data = load_data, url = load_url)


@app.route('/get-load-json')
def get_load_json():
    """
        Fetches the application and models load data from all the virtual VMs
    """
    url = module_config['deployer_master']
    response = requests.get(f'{url}get-load')
    load_data = jsonify(json.loads(response.content.decode('utf-8')))
    return load_data


def start():
    app.run(host='0.0.0.0', port=5000)
