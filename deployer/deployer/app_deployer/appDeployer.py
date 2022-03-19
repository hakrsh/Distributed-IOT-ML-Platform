import json


def run(package, sensor_id):
    import zipfile
    with zipfile.ZipFile(package, 'r') as zip_ref:
        zip_ref.extractall('app_deployer')
    print("Extracted package")
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
    with open('app_deployer/app/src/getdata.py', 'w') as f:
        f.write(sensorStub)

    return container_name
