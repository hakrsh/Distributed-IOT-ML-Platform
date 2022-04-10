import logging
logging.basicConfig(level=logging.INFO)


def run(package, model_id):
    import zipfile
    with zipfile.ZipFile(package, 'r') as zip_ref:
        zip_ref.extractall('/tmp/'+model_id)
    logging.info('Extracted package: ' + package)

    # generate server.py
    server_code = ''
    server_code += "from flask import Flask, request\n"
    server_code += "from preprocessing import preprocess\n"
    server_code += "from postprocessing import postprocess\n"
    server_code += "app = Flask(__name__)\n"
    server_code += "\n"
    server_code += "@app.route('/')\n"
    server_code += "def index():\n"
    server_code += "    return 'Model is running!'\n"
    server_code += "\n"
    server_code += "@app.route('/get-pred', methods=['POST'])\n"
    server_code += "def get_pred():\n"
    server_code += "    data = preprocess(request.json)\n"
    server_code += "    model=None\n"
    server_code += "    try:\n"
    server_code += "        import pickle\n"
    server_code += "        model = pickle.load(open('model.pkl', 'rb'))\n"
    server_code += "    except:\n"
    server_code += "        from keras.models import load_model\n"
    server_code += "        model = load_model('model.h5')\n"
    server_code += "    pred = model.predict(data)\n"
    server_code += "    return postprocess(pred)\n"
    server_code += "\n"
    server_code += "if __name__ == \"__main__\":\n"
    server_code += "    app.run(host='0.0.0.0', port=80)\n"
    logging.info('Generated server.py')

    with open(f'/tmp/{model_id}/model/server.py', 'w') as f:
        f.write(server_code)
    logging.info('Wrote server.py')

    dockerfile = """FROM python:3
ADD model model
WORKDIR /model
RUN pip install -r requirements.txt
EXPOSE 80
CMD [ "python3","server.py" ]"""

    with open(f'/tmp/{model_id}/Dockerfile', 'w') as f:
        f.write(dockerfile)
    logging.info('Wrote Dockerfile')
    logging.info('Ready to build the model image')
