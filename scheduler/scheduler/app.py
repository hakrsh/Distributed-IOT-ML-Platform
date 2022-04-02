from distutils.log import debug
from flask import Flask, render_template, request
import requests
from datetime import datetime
import json
import scheduler.sched as sh
import threading
from scheduler import app, module_config




def get_sensor_data():
    
    """ To request sensor details from sensor team"""
    try:
        # sensor_data = requests.get(f"{module_config['sensor_api']}getAllSensors")
        # print(sensor_data.json())
        sensor_data = [{"sensor_type":"heat", "sensor_location":"Hyderabad", "sensor_id":"1234"},
                    {"sensor_type":"temperature", "sensor_location":"Mumbai", "sensor_id":"1235"},
                    {"sensor_type":"humidity", "sensor_location":"Chennai", "sensor_id":"1236"},
                    {"sensor_type":"light", "sensor_location":"Banglore", "sensor_id":"1237"}]
        return sensor_data
         # sample api from application manager
        return sensor_data.json()
    except Exception as e:
        print(e)
    # sensor_data = [{"sensor_type":"heat", "sensor_location":"Hyderabad", "sensor_id":"1234"},
    #                 {"sensor_type":"heat", "sensor_location":"Mumbai", "sensor_id":"1235"},
    #                 {"sensor_type":"heat", "sensor_location":"Chennai", "sensor_id":"1236"}]
    # return sensor_data


def get_app_data():

    """To request apps name from the storage team"""
    try:
        # apps_name = requests.get(f'{module_config["platform_api"]}/api/get-applications')
        # print(apps_name.json())
        apps_name = [ 
            { 
            'ApplicationID': '87160e53-5fb4-411c-bd20-8ecbb3c6e7a5', 
            'ApplicationName': 'MobileUploadTest', 
            'Contract': 
                {'name': 'titanic_app',
                "sensors":[
                    {
                        "function" : "getheat",
                        "sensor_type" : "heat"
                    },
                    {
                        "function" : "gethumidity",
                        "sensor_type" : "humidity"
                    },
                    {
                        "function" : "getlight",
                        "sensor_type" : "light"
                    },
                    {
                        "function" : "gettemperature",
                        "sensor_type" : "temperature"
                    }
                ] ,
                'endpoint': '/app/app.py'
                }
            }, 
            {'ApplicationID': '58c5c0eb-e5c4-4d00-86a1-8c6f6fbfaf52', 
            'ApplicationName': 'Test', 
            'Contract': 
                {'name': 'titanic_app', 
                "sensors":[
                    {
                        "function" : "getlight",
                        "sensor_type" : "light"
                    },
                    {
                        "function" : "gettemperature",
                        "sensor_type" : "temperature"
                    }
                ],
                'endpoint': '/app/app.py'
                }
            }
        ]
        return apps_name
        # return apps_name.json()
    except Exception as e:
        print(e)
    # apps_name = [{"ApplicationID":1234,"ApplicationName":"xxx jjjj"},
    #             {"ApplicationID":1234,"ApplicationName":"yyy"}]
    # return apps_name

"""Get the data from sensor and storage team"""
def refresh_data():
    print("Refreshing data")
    app_data = get_app_data()
    sensor_data = get_sensor_data()
    data = dict()
    data["app"] = app_data
    data["sensor"] = sensor_data
    # print(app_data)
    return data


@app.route('/')
def home():
    """
        The home page of the application
        Fetches application data using refresh_data() function and displays it in the form
    """
    data = refresh_data()
    app_data = data["app"]
    sensor_data = data["sensor"]
    app_lst = [{app['ApplicationID']:app['ApplicationName']} for app in app_data]
    # app_lst = list(dict.fromkeys(app_lst))
    # print(app_data,app_lst)
    sensor_type = [sensor['sensor_type'] for sensor in sensor_data]
    sensor_type = list(dict.fromkeys(sensor_type))
    sensor_loc = [sensor['sensor_location'] for sensor in sensor_data]
    sensor_loc = list(dict.fromkeys(sensor_loc))
    sensors = [sensor['sensor_type'] + "-" + sensor['sensor_location'] for sensor in sensor_data]
    return render_template ("index.html", app_list = app_lst, sensors = sensors)



@app.route('/get_app_contract',methods =["POST"])  
def get_app_contract():


    app_id = json.loads(request.get_data())["app_id"]
    print(app_id)

    data = refresh_data()
    app_data = data["app"]
    sensor_data = data["sensor"]


    list_of_sensors = [[sensor["sensor_id"],sensor['sensor_type'],sensor['sensor_location']] for sensor in sensor_data]




    req_sensors = []
    for app in app_data:
        if(app["ApplicationID"] == app_id):
            req_sensors = app["Contract"]["sensors"]
    


    
    sensors_of_app = {}
    for sensor in req_sensors:

        type_of_sensor = sensor["sensor_type"]
        if(type_of_sensor in sensors_of_app):
            sensors_of_app[type_of_sensor][0] +=1
        else:

            sensors_list = []
            for type in list_of_sensors:
                if(type[1] == type_of_sensor):
                    sensors_list.append(type[0])
                    sensors_list.append(type[1])

            sensors_of_app[type_of_sensor] = [1,[]]
            sensors_of_app[type_of_sensor][1] = sensors_list

    sensors_of_app_send =[]
    for k,v in sensors_of_app.items():
        d={}
        d["sensor_type"] = k
        d["sensors_list"] = v[1]
        d["count"] = v[0]
        sensors_of_app_send.append(d)


    print(sensors_of_app_send)
    return json.dumps(sensors_of_app_send)




    


@app.route('/schedule', methods = ['POST'])
def schedule():
    """
        This will run once the form is submitted

        Will extract application location and sensor id and call the function that schedules
        the deployment.
    """
    refresh_data()
    data = refresh_data()
    app_data = data["app"]
    print(app_data)
    sensor_data = data["sensor"]
    app_name = request.form['app_name']
    time = request.form['datetime']
    my_sensors = request.form.getlist('my_sensors')
    time = time.replace('T',' ')
    time = time+":00"
    time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    sensor_id = []
    print("selected sensors", my_sensors)
    print('app_name: ', app_name)
    for s in my_sensors:
        s_type, loc = s.split("-")
        res = [sensor for sensor in sensor_data if sensor["sensor_type"]==s_type and sensor["sensor_location"]==loc]
        sensor_id.append(res[0]["sensor_id"])
    app_id,app_loc = 0,0
    for app_dict in app_data:
        if(app_name == app_dict["ApplicationName"]):
            app_id  = app_dict["ApplicationID"]
    print(sensor_id)
    print('app_id: ' ,app_id)
    query = {
    "ApplicationID":app_id,
    "sensor_ids":sensor_id
    }
    # print(query["sensor_ids"])
    msg = sh.schedule_a_task(time,query=query)
    print(msg)
    return render_template ("deploy.html", time = time)


def start():
    t = threading.Thread(target=sh.run_schedule)
    t.daemon = True
    t.start()
    app.run(debug=True,port = 8210,host='0.0.0.0')