from cmath import log
import json
import logging
logging.basicConfig(level=logging.INFO)


def run(package, sensor_id):
    import zipfile
    with zipfile.ZipFile(package, 'r') as zip_ref:
        zip_ref.extractall('app_deployer')
    logging.info('Extracted package: {}'.format(package))
    contract = json.load(open('app_deployer/app/app_contract.json'))
    container_name = contract['name']
    # generate getdata.py inside app/src
    sensorStub = ''
    sensorStub += "import requests\n"
    sensorStub += "import json\n"
    sensorStub += 'def get_data():\n'
    sensorStub += "    url = 'http://10.1.38.47:7000/data/" + sensor_id + "'\n"
    sensorStub += "    r = requests.get(url)\n"
    sensorStub += "    return json.loads(r.text)\n"
    logging.info('Generated getdata.py')
    with open('app_deployer/app/src/getdata.py', 'w') as f:
        f.write(sensorStub)
    logging.info('Wrote getdata.py')
    logging.info('Ready to build the app image')
    return container_name
