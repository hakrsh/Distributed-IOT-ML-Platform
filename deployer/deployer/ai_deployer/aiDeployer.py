import json
import logging
from tkinter import image_names
logging.basicConfig(level=logging.INFO)


def run(package, model_id):
    import zipfile
    with zipfile.ZipFile(package, 'r') as zip_ref:
        zip_ref.extractall('/tmp/'+model_id)
    logging.info('Extracted package: ' + package)

    contract = json.load(open(f'/tmp/{model_id}/model/model_contract.json'))
    port = contract['port']
    endpoint = contract['endpoint']
    image_name = contract['name']
    # generate server.py
    server_code = ''
    server_code += "from flask import Flask, request\n"
    server_code += "import pickle\n"
    server_code += "from preprocessing import preprocess\n"
    server_code += "from postprocessing import postprocess\n"
    server_code += "app = Flask(__name__)\n"
    server_code += "\n"
    server_code += "@app.route('/')\n"
    server_code += "def index():\n"
    server_code += "    return 'Model is running!'\n"
    server_code += "\n"
    server_code += f"@app.route('/{endpoint}', methods=['POST'])\n"
    server_code += f"def {endpoint}():\n"
    server_code += "    data = preprocess(request.json)\n"
    server_code += "    modelfile = open('model.pkl', 'rb')\n"
    server_code += "    model = pickle.load(modelfile)\n"
    server_code += "    pred = model.predict(data)\n"
    server_code += "    return postprocess(pred)\n"
    server_code += "\n"
    server_code += "if __name__ == \"__main__\":\n"
    server_code += f"    app.run(host='0.0.0.0', port={int(port)})\n"
    logging.info('Generated server.py')

    with open(f'/tmp/{model_id}/model/server.py', 'w') as f:
        f.write(server_code)
    logging.info('Wrote server.py')

    dockerfile = """FROM python:3
ADD model model
WORKDIR /model
RUN pip install -r requirements.txt
CMD [ "python3","server.py" ]"""

    with open(f'/tmp/{model_id}/Dockerfile', 'w') as f:
        f.write(dockerfile)
    logging.info('Wrote Dockerfile')
    logging.info('Ready to build the model image')
    return image_name
