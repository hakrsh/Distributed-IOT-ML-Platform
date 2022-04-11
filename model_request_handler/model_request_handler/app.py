from flask import request
import requests
from model_request_handler import app, db, models
import logging
import json 
logging.basicConfig(level=logging.INFO)

def get_running_models():
    instances = db.instances
    # if there any changes in instances collections update models hashmap
    for change in instances.watch():
        if change["operationType"] == "update":
            logging.info('update detected')
            document_id = change['documentKey']
            document = instances.find_one(document_id)
            if document['type'] == 'model' and document['status'] == 'running':
                logging.info('Model Name: {}'.format(document['model_name']))
                url = f'http://{document["ip"]}:{document["port"]}/get-pred'
                logging.info(f'url: {url}')
                models[document['model_id']] = url
                logging.info('models hashmap updated')
                with open('models.json', 'w') as f:
                    json.dump(models, f)

@app.route('/')
def index():
    return 'Model request handler running!'

@app.route('/<ModelId>', methods=['POST'])
def get_model(ModelId):
    logging.info('ModelId: ' + ModelId)
    if ModelId in models:    
        url = models[ModelId]
        res = requests.post(url, json=request.json)
        return res.text
    else:
        return 'Model not found'

@app.route('/get-all-models', methods=['GET'])
def get_all_models():
    return models

def start():
    app.run(host='0.0.0.0', port=5050)
