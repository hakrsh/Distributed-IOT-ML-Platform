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
        sensor_data = requests.get(f"{module_config['sensor_api']}getAllSensors")
        print(sensor_data.json())
        return sensor_data.json()
        # return json.loads(sensor_data.json())
    except:
        print("Error")
    # sensor_data = [{"sensor_type":"heat", "sensor_location":"Hyderabad", "sensor_id":"1234"},
    #                 {"sensor_type":"heat", "sensor_location":"Mumbai", "sensor_id":"1235"},
    #                 {"sensor_type":"heat", "sensor_location":"Chennai", "sensor_id":"1236"}]
    # return sensor_data


def get_app_data():

    """To request apps name from the storage team"""
    try:
        apps_name = requests.get(f'{module_config["platform_api"]}/api/get-applications')
        print(apps_name.json())
        return apps_name.json()
        # return json.loads(apps_name.json())
    except:
        print("Error")
    # apps_name = [{"ApplicationID":1234,"ApplicationName":"xxx","FileLocation":"c:/Downloads"},
    #             {"ApplicationID":1234,"ApplicationName":"yyy","FileLocation":"c:/Downloads"}]
    # return apps_name

"""Get the data from sensor and storage team"""
def refresh_data():
    print("Refreshing data")
    app_data = get_app_data()
    sensor_data = get_sensor_data()
    data = dict()
    data["app"] = app_data
    data["sensor"] = sensor_data
    print(app_data)
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
    app_lst = [app['ApplicationName'] for app in app_data]
    app_lst = list(dict.fromkeys(app_lst))
    sensor_type = [sensor['sensor_type'] for sensor in sensor_data]
    sensor_type = list(dict.fromkeys(sensor_type))
    sensor_loc = [sensor['sensor_location'] for sensor in sensor_data]
    sensor_loc = list(dict.fromkeys(sensor_loc))
    sensors = [sensor['sensor_type'] + "-" + sensor['sensor_location'] for sensor in sensor_data]
    return render_template ("index.html", app_list = app_lst, sensors = sensors)


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
            app_loc  = app_dict["ApplicationID"]
    print(sensor_id)
    print('app_loc: ' ,app_loc)
    query = {
    "ApplicationID":app_loc,
    "sensor_ids":sensor_id
    }
    print(query["sensor_ids"])
    msg = sh.schedule_a_task(time,query=query)
    print(msg)
    return render_template ("deploy.html", time = time)


def start():
    t = threading.Thread(target=sh.run_schedule)
    t.daemon = True
    t.start()
    app.run(port = 8210,host='0.0.0.0')