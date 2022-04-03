import json
from deployer import module_config
import logging
logging.basicConfig(level=logging.INFO)


def run(package, sensors, app_id):
    import zipfile
    with zipfile.ZipFile(package, 'r') as zip_ref:
        zip_ref.extractall('/tmp/'+app_id)
    logging.info('Extracted package: ' + package)
    contract = json.load(open(f'/tmp/{app_id}/app/app_contract.json'))
    image_name = contract['name']
    # generate getdata.py inside app/src
    sensorStub = ''
    sensorStub += "import requests\n"
    sensorStub += "import json\n"
    for sensor in sensors:
        sensorStub += f'def {sensor["function"]}():\n'
        sensorStub += '    url = "{}data/{}"\n'.format(
            module_config['sensor_api'], sensor['sensor_id'])
        sensorStub += "    r = requests.get(url)\n"
        sensorStub += "    return json.loads(r.text)\n"
    logging.info('Generated getdata.py')
    with open(f'/tmp/{app_id}/app/src/getdata.py', 'w') as f:
        f.write(sensorStub)
    logging.info('Wrote getdata.py')

    dockerfile = """FROM python:3
ADD app app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 80
CMD ["python3", "src/app.py","model_contract.json"]"""

    with open(f'/tmp/{app_id}/Dockerfile', 'w') as f:
        f.write(dockerfile)
    logging.info('Wrote Dockerfile')
    logging.info('Ready to build the app image')
    return image_name
