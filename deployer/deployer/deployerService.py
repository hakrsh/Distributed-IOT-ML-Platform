import os
import shutil
from flask import request
from deployer.ai_deployer import aiDeployer
from deployer.app_deployer import appDeployer
from deployer.deploy import Deploy
from . import app, db


@app.route('/')
def index():
    return 'Deployer is running!'


@app.route('/model', methods=['POST'])
def deploy_model():
    ModelId = request.json['ModelId']
    model = db.models.find_one({"ModelId": ModelId})
    with open('/tmp/model.zip', 'wb') as f:
        f.write(model['content'])
    container_name = aiDeployer.run('/tmp/model.zip')
    res = Deploy(path='ai_deployer', container_name=container_name)
    os.remove('/tmp/model.zip')
    shutil.rmtree('ai_deployer/model')
    return res


@app.route('/app', methods=['POST'])
def deploy_app():
    ApplicationID = request.json['ApplicationID']
    print(ApplicationID)
    sensor_id = str(request.json['sensor_ids'][0])
    application = db.applications.find_one({"ApplicationID": ApplicationID})
    with open('/tmp/app.zip', 'wb') as f:
        f.write(application['content'])
    container_name = appDeployer.run('/tmp/app.zip', sensor_id)
    res = Deploy(path='app_deployer', container_name=container_name)
    os.remove('/tmp/app.zip')
    shutil.rmtree('app_deployer/app')
    return res


def start():
    app.run(port=9999, host='0.0.0.0')
