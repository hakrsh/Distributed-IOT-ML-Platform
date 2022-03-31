import json
from flask import request, render_template
import requests
import uuid
from platform_manager import app,db,module_config
import logging
import zipfile
import os
import shutil

logging.basicConfig(level=logging.INFO)


@app.route('/')
def index():
    return 'Platform manager running!'

@app.route('/upload-model', methods=['GET','POST'])
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
        db.models.insert_one({"ModelId": ModelId, "ModelName": model_name, "content": content, "model_contract": model_contract})
        logging.info('Model uploaded successfully')
        url = module_config['deployer'] + '/model'
        logging.info('Sending model to deployer')
        response = requests.post(url, json={"ModelId":ModelId}).content
        return response.decode('ascii')

@app.route('/get-model/<ModelId>', methods=['GET'])
def get_model(ModelId):
    model = db.models.find_one({"ModelId":ModelId})
    return {'ModelId': model['ModelId'], 'ModelName': model['ModelName'], 'model_contract': model['model_contract']}
@app.route('/get-models', methods=['GET'])

def get_models():
    models = db.models.find()
    data = []
    for model in models:
        data.append({'ModelId': model['ModelId'], 'ModelName': model['ModelName'], 'model_contract': model['model_contract']})
    return json.dumps(data)

@app.route('/upload-app', methods=['POST','GET'])
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
        model_id = 'c9524b51-28ce-4802-b082-7c120805413e' #TODO get it from front end
        model = get_model(model_id)
        with open('/tmp/' + ApplicationID + '/app/model_contract.json', 'w') as f:
            json.dump(model['model_contract'], f)
        logging.info('Inserted model contract into app')
        shutil.make_archive('/tmp/' + ApplicationID, 'zip', '/tmp/'+ ApplicationID)
        with open('/tmp/' + ApplicationID + '.zip', 'rb') as f:
            content = f.read()
        # os.remove('/tmp/' + ApplicationID + '.zip')
        logging.info('Application zip removed')
        shutil.rmtree('/tmp/' + ApplicationID)
        logging.info('Application temp directory removed')
        db.applications.insert_one({"ApplicationID": ApplicationID, "ApplicationName": ApplicationName, "content": content, "app_contract": app_contract})
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
    data = {'ApplicationID': application['ApplicationID'], 'ApplicationName': application['ApplicationName'], 'Contract': application['app_contract']}
    return json.dumps(data)

def start():
    app.run(host='0.0.0.0',port=5000)
# if __name__ == '__main__':
#     app.run(host='0.0.0.0',port=5000)
