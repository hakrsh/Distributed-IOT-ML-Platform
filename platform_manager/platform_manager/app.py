import json
from flask import request, render_template
from bson.json_util import dumps
import requests
import time
from platform_manager import app,db,module_config


@app.route('/')
def index():
    return 'Platform manager running!'

@app.route('/upload-model', methods=['GET','POST'])
def upload_model():
    if request.method == 'GET':
        return render_template('upload_model.html')
    elif request.method == 'POST':
        model_name = request.form['model_name']
        ModelId = str(round(time.time()))
        content = request.files['file'].read()
        db.models.insert_one({"ModelId": ModelId, "ModelName": model_name, "content": content})
        url = module_config['deployer'] + '/model'
        response = requests.post(url, json={"ModelId":ModelId}).content
        return response.decode('ascii')

@app.route('/upload-app', methods=['POST','GET'])
def upload_app():
    if request.method == 'GET':
        return render_template('upload_app.html')
    if request.method == 'POST':
        data = request.form
        ApplicationID = str(round(time.time()))
        print(ApplicationID)
        ApplicationName = data['ApplicationName']
        content = request.files['file'].read()
        db.applications.insert_one({"ApplicationID": ApplicationID, "ApplicationName": ApplicationName, "content": content})
        return 'Application stored successfully'

@app.route('/api/get-applications', methods=['GET'])
def fetch_applications():
    applications = db.applications.find()
    data = []
    for application in applications:
        temp = {}
        temp['ApplicationID'] = application['ApplicationID']
        temp['ApplicationName'] = application['ApplicationName']
        data.append(temp)
    return json.dumps(data)

@app.route('/api/get-application/<ApplicationID>', methods=['GET'])
def fetch_application(ApplicationID):
    application = db.applications.find_one({"ApplicationID": ApplicationID})
    data = {'ApplicationID': application['ApplicationID'], 'ApplicationName': application['ApplicationName']}
    return json.dumps(data)

def start():
    app.run(host='0.0.0.0',port=5000)
# if __name__ == '__main__':
#     app.run(host='0.0.0.0',port=5000)
