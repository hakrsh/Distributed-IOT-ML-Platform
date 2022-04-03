import json
from flask import request, render_template, url_for, jsonify
import requests
import uuid
from platform_manager import app, db, module_config
import logging
import zipfile
import os
import shutil

logging.basicConfig(level=logging.INFO)


@app.route('/')
def index():
    return 'Platform manager running!'


@app.route('/upload-model', methods=['GET', 'POST'])
def upload_model():
    if request.method == 'GET':
        return render_template('upload_model.html')
    elif request.method == 'POST':
        model_name = request.form['model_name']
        ModelId = str(uuid.uuid4())
        logging.info('ModelId: ' + ModelId)
        content = request.files['file'].read()
        with open('/tmp/' + ModelId + '.zip', 'wb') as f:
            f.write(content)
        logging.info('Model saved to /tmp/' + ModelId + '.zip')
        with zipfile.ZipFile('/tmp/' + ModelId + '.zip', 'r') as zip_ref:
            zip_ref.extractall('/tmp/' + ModelId)
        logging.info('Model extracted to /tmp/' + ModelId)
        model_contract = {}
        with open('/tmp/' + ModelId + '/model/model_contract.json', 'r') as f:
            model_contract = json.load(f)

        logging.info('Model contract uploaded successfully')
        os.remove('/tmp/' + ModelId + '.zip')
        logging.info('Model zip removed')
        shutil.rmtree('/tmp/' + ModelId)
        logging.info('Model temp directory removed')
        db.models.insert_one({"ModelId": ModelId, "ModelName": model_name,
                             "content": content, "model_contract": model_contract})
        logging.info('Model uploaded successfully')
        url = module_config['deployer'] + '/model'
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
            data.append({'instance_id': instance['instance_id'],
                        'model_id': instance['model_id'], 'ModelName': model['ModelName']})
    return json.dumps(data)


@app.route('/upload-app', methods=['POST', 'GET'])
def upload_app():
    if request.method == 'GET':
        return render_template('upload_app.html')
    if request.method == 'POST':
        data = request.form
        ApplicationID = str(uuid.uuid4())
        ApplicationName = data['ApplicationName']
        content = request.files['file'].read()
        with open('/tmp/' + ApplicationID + '.zip', 'wb') as f:
            f.write(content)
        logging.info('Application saved to /tmp/' + ApplicationID + '.zip')
        with zipfile.ZipFile('/tmp/' + ApplicationID + '.zip', 'r') as zip_ref:
            zip_ref.extractall('/tmp/' + ApplicationID)
        logging.info('Application extracted to /tmp/' + ApplicationID)
        app_contract = {}
        with open('/tmp/' + ApplicationID + '/app/app_contract.json', 'r') as f:
            app_contract = json.load(f)
        # TODO get it from front end
        running_models = json.loads(get_running_models())
        logging.info('Chosing a random model')
        model_id = running_models[0]['model_id']
        model_instance_id = running_models[0]['instance_id']
        logging.info('model_id: ' + model_id)
        logging.info('model_instance_id: ' + model_instance_id)
        model_config = requests.get('http://localhost:5000/get-running-model-config',json={"model_id": model_id, "instance_id": model_instance_id}).json()
        with open('/tmp/' + ApplicationID + '/app/model_contract.json', 'w') as f:
            json.dump(model_config, f)
        logging.info('Inserted model contract into app')
        shutil.make_archive('/tmp/' + ApplicationID,
                            'zip', '/tmp/' + ApplicationID)
        with open('/tmp/' + ApplicationID + '.zip', 'rb') as f:
            content = f.read()
        # os.remove('/tmp/' + ApplicationID + '.zip')
        logging.info('Application zip removed')
        shutil.rmtree('/tmp/' + ApplicationID)
        logging.info('Application temp directory removed')
        db.applications.insert_one(
            {"ApplicationID": ApplicationID, "ApplicationName": ApplicationName, "content": content, "app_contract": app_contract})
        logging.info('Application uploaded successfully')
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
    url = module_config['deployer']
    print(url)
    print((f'{url}get-load'))
    response = requests.get(f'{url}get-load')
    load_url = url+"get-load"

    load_data = json.loads(response.content.decode('utf-8'))
    
    print(type(load_data))
    
    return render_template ("load-data.html", load_data = load_data, url = load_url)

def start():
    app.run(host='0.0.0.0', port=5000)
