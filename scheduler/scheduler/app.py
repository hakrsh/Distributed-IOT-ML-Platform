from distutils.log import debug
from flask import Flask, render_template, request
import requests
from datetime import datetime
from datetime import timedelta
import json
import uuid
import scheduler.sched as sh
import threading
from scheduler import app, module_config, db, client
import logging


logging.basicConfig(        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)


def get_sensor_data():
    
    """ To request sensor details from sensor team"""
    try:
        sensor_data = requests.get(f"{module_config['sensor_api']}getAllSensors")
        return sensor_data.json()
    except Exception as e:
        logging.error(e)


def get_app_data():

    """To request apps name from the storage team"""
    try:
        apps_name = requests.get(f'{module_config["platform_api"]}/api/get-applications')
        return apps_name.json()
    except Exception as e:
        logging.error(e)

"""Get the data from sensor and storage team"""
def refresh_data():
    logging.info("Refreshing data from APIs")
    app_data = get_app_data()
    sensor_data = get_sensor_data()
    data = dict()
    data["app"] = app_data
    data["sensor"] = sensor_data
    return data

def insert_into_db(app_id, app_name, sensor_info, start_time, end_time):
    logging.info("Inserting into db")
    try:
        sched_id = str(uuid.uuid4())
        ref = db.scheduleinfo.insert_one({"sched_id":sched_id, 
                                            "Application_ID":app_id, 
                                            "app_name":app_name,
                                            "sensor_info":sensor_info, 
                                            "start_time":str(start_time),
                                            "end_time":str(end_time), 
                                            "instance_id":"blank", 
                                            "stopped_flag": False})
        return sched_id
    except Exception as e:
        logging.error(e)

@app.route('/')
def home():
    """
        The home page of the application
        Fetches application data using refresh_data() function and displays it in the form
    """
    logging.info("Running scheduler")
    data = refresh_data()
    app_data = data["app"]
    sensor_data = data["sensor"]
    # app_lst = [app['ApplicationName'] for app in app_data]
    # app_lst = list(dict.fromkeys(app_lst))
    app_lst = [{app['ApplicationID']:app['ApplicationName']} for app in app_data]
    sensor_type = [sensor['sensor_type'] for sensor in sensor_data]
    sensor_type = list(dict.fromkeys(sensor_type))
    sensor_loc = [sensor['sensor_location'] for sensor in sensor_data]
    sensor_loc = list(dict.fromkeys(sensor_loc))
    sensors = [sensor['sensor_type'] + "-" + sensor['sensor_location'] for sensor in sensor_data]
    return render_template ("index.html", app_list = app_lst, sensors = sensors)
  

def format_time(time):
    time = time.replace('T',' ')
    time = time+":00"
    time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    return time

@app.route('/schedule', methods = ['POST'])
def schedule():
    """
        This will run once the form is submitted

        Will extract application location and sensor id and call the function that schedules
        the deployment.
    """
    refresh_data()
    data = refresh_data()
    logging.info("Reading form data")
    app_data = data["app"]
    sensor_data = data["sensor"]
    app_id = request.form['app_name']
    start_time = request.form['starttime']
    end_time = request.form['endtime']
    my_sensors = request.form.getlist('my_sensors')
    logging.info("User selected data: " + str(app_id) + str(my_sensors) + str(start_time) + str(end_time))
    start_time = format_time(start_time)
    end_time = format_time(end_time)
    delta,time_to_execute = sh.get_scheduled_time(start_time)
    if(delta=="Invalid time"):
        error_msg = "Invalid Time"
        return render_template("error.html", error_msg=error_msg)
    if end_time < start_time:
        error_msg = "End time is less than start time"
        return render_template("error.html", error_msg=error_msg)
    sensor_info = {}
    for s in my_sensors:
        s_type, loc, s_id = s.split("-")
        if s_type not in sensor_info.keys():
            sensor_info[s_type] = [s_id]
        else:
            sensor_info[s_type].append(s_id)

    req_func = []
    for app_dict in app_data:
        if(app_id == app_dict["ApplicationID"]):
            app_name = app_dict["ApplicationName"]
            req_func = app_dict["Contract"]["sensors"]
            break
    

    func_of_sensors = {}
    for sensor in req_func:
        type_of_sensor = sensor["sensor_type"]
        if(type_of_sensor in func_of_sensors):
            func_of_sensors[type_of_sensor].append(sensor["function"])
        else:
            func_of_sensors[type_of_sensor] = []
            func_of_sensors[type_of_sensor].append(sensor["function"])
    sensor_to_func_mapping =[]
    for sensor_type,funcs in func_of_sensors.items():      
        for i in range(len(funcs)):
            d = {}
            if(len(sensor_info[sensor_type]) == len(func_of_sensors[sensor_type])):
                d["sensor_id"] = sensor_info[sensor_type][i]
                d["function"] = funcs[i]
                sensor_to_func_mapping.append(d)
            else:
                error_msg = "select required number of sensors"
                return render_template("error.html", error_msg=error_msg)

    # print(sensor_to_func_mapping)
    logging.info("Sending data to deployer: " + str(app_id) + str(sensor_info))
    sched_id = insert_into_db(app_id, app_name, sensor_to_func_mapping, start_time, end_time)
    query = {
        "type": "app",
        "ApplicationID":app_id,
        "app_name":app_name,
        "sensor_ids":sensor_to_func_mapping,
        "sched_id":sched_id
    }
    print(query)
    msg = sh.schedule_a_task(start_time, end_time, query=query)
    print(msg)
    return render_template ("deploy.html", time = start_time)

@app.route('/reschedule/<instance_id>', methods = ["GET"])
def reshedule(instance_id):
    app_data = db.scheduleinfo.find_one({"instance_id":instance_id})
    start_time = datetime.now() + timedelta(seconds=2)
    end_time = datetime.strptime(app_data["end_time"], '%Y-%m-%d %H:%M:%S')
    new_sched_id = insert_into_db(app_data["Application_ID"], app_data["app_name"], app_data["sensor_info"], start_time, end_time)
    query = {
        "type":"app",
        "ApplicationID":app_data["Application_ID"],
        "app_name":app_data["app_name"],
        "sensor_ids":app_data["sensor_info"],
        "sched_id":new_sched_id
    }
    print(query)
    response = requests.post(f"{module_config['deployer_master']}app",json=query)
    response = json.loads(response.text)
    new_instance_id = response["InstanceID"]
    sh.update_instance_id(new_instance_id, new_sched_id)
    sh.schedule_a_stop_task(end_time, {"instance_id":new_instance_id})
    return str(new_instance_id)

@app.route('/get_app_contract',methods =["POST"])  
def get_app_contract():
    app_id = json.loads(request.get_data())["app_id"]
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
                    sensors_list.append([type[0],type[2]])

            sensors_of_app[type_of_sensor] = [1,[]]
            sensors_of_app[type_of_sensor][1] = sensors_list

    sensors_of_app_send =[]
    for k,v in sensors_of_app.items():
        d={}
        d["sensor_type"] = k
        d["sensors_list"] = v[1]
        d["count"] = v[0]
        sensors_of_app_send.append(d)

    return json.dumps(sensors_of_app_send)


def schedule_pending_tasks():
    pending_tasks = db.scheduleinfo.find({"instance_id":"blank"})
    for task in pending_tasks:
        query = {
            "ApplicationID":task["Application_ID"],
            "app_name":task["app_name"],
            "sensor_ids":task["sensor_info"],
            "sched_id":task["sched_id"]
        }
        start_time = datetime.strptime(task["start_time"], '%Y-%m-%d %H:%M:%S')
        if datetime.now() <= start_time:
            end_time = datetime.strptime(task["end_time"], '%Y-%m-%d %H:%M:%S')
            msg = sh.schedule_a_task(start_time, end_time, query=query)
    
    pending_tasks = db.scheduleinfo.find({"stopped_flag":False})
    for task in pending_tasks:
        if task["instance_id"] != "blank":
            query = {
                "instance_id":task["instance_id"]
            }
            end_time = datetime.strptime(task["end_time"], '%Y-%m-%d %H:%M:%S')
            if datetime.now() <= end_time:
                msg = sh.schedule_a_stop_task(end_time, query=query)


def start():
    t = threading.Thread(target=sh.run_schedule)
    t.daemon = True
    t.start()
    pending_jobs = threading.Thread(target = schedule_pending_tasks)
    pending_jobs.start()
    app.run(debug=True, port = 8210, host='0.0.0.0')
