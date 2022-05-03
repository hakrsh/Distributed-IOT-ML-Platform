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

db_sensors = client["sensors"]
sensor_config = db_sensors["sensordetails"]
controller_config = db_sensors["controllerdetails"]
db_app = client.repo

def get_sensor_data():
    
    """ To request sensor details from sensor team"""
    try:
        sensors_cursor = sensor_config.find({})
        list_of_sensors = []
        for document in sensors_cursor:
            sensorinfo = {}
            sensorinfo["sensor_id"] = document["topic_id"]
            sensorinfo["sensor_type"] = document["Type"]
            sensorinfo["sensor_location"] = document["Location"]
            list_of_sensors.append(sensorinfo)
        return list_of_sensors
    except Exception as e:
        logging.error(e)

def get_controller_data():
    
    """ To request controller details from controller team"""
    try:
        controllers_cursor = controller_config.find({})
        list_of_controllers = []
        for document in controllers_cursor:
            controllerinfo = {}
            controllerinfo["controller_id"] = document["controller_id"]
            controllerinfo["controller_type"] = document["Type"]
            controllerinfo["controller_location"] = document["Location"]
            list_of_controllers.append(controllerinfo)
        return list_of_controllers
    except Exception as e:
        logging.error(e)


def get_app_data():

    """To request apps name from the storage team"""
    try:

        app_cursor = db_app.applications.find({})
        apps_name = []
        for document in app_cursor:
            appinfo = {}
            appinfo["ApplicationID"] = document["ApplicationID"]
            appinfo["ApplicationName"] = document["ApplicationName"]
            appinfo["Contract"] = document["app_contract"]
            apps_name.append(appinfo)
        return apps_name
    except Exception as e:
        logging.error(e)

"""Get the data from sensor and storage team"""
def refresh_data():
    logging.info("Refreshing data from APIs")
    app_data = get_app_data()
    sensor_data = get_sensor_data()
    controller_data = get_controller_data()
    data = dict()
    data["app"] = app_data
    data["sensor"] = sensor_data
    data["controller"] = controller_data
    return data

def insert_into_db(app_id, app_name, sensor_info, controller_info, start_time, end_time):
    logging.info("Inserting into db")
    try:
        sched_id = str(uuid.uuid4())
        ref = db.scheduleinfo.insert_one({"sched_id":sched_id, 
                                            "Application_ID":app_id, 
                                            "app_name":app_name,
                                            "sensor_info":sensor_info, 
                                            "controller_info": controller_info,
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
    app_lst = [{app['ApplicationID']:app['ApplicationName']} for app in app_data]
    return render_template ("index.html", app_list = app_lst)
  

def format_time(time):
    time = time.replace('T',' ')
    time = time+":00"
    time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    return time

def assign_random(app_id, s_loc, c_loc):
    app_data = db.app_spec_data.find_one({"app_id":app_id})
    sloc_data = db.temp_data.find_one({"app_id":app_id, "type":"sensor"})
    sloc_data = sloc_data["data"][s_loc]
    cloc_data = db.temp_data.find_one({"app_id":app_id, "type":"controller"})
    cloc_data = cloc_data["data"][c_loc]
    sensor_list = {}
    for sensor in app_data["data"]["sensor"]:
        stype = sensor["sensor_type"]
        count = sensor["count"]
        sensor_list[stype] = sloc_data[stype][:count]
    controller_list = {}
    for controller in app_data["data"]["controller"]:
        ctype = controller["controller_type"]
        count = controller["count"]
        controller_list[ctype] = cloc_data[ctype][:count]
    db.temp_data.delete_one({"app_id":app_id, "type":"sensor"})
    db.temp_data.delete_one({"app_id":app_id, "type":"controller"})
    db.app_spec_data.delete_one({"app_id":app_id})
    return sensor_list, controller_list

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
    option_selected = request.form['selectoption']
    if option_selected == 'specific':
        my_sensors = request.form.getlist('my_sensors')
        my_controllers = request.form.getlist('my_controllers')
        logging.info("User selected data: " + str(app_id) + str(my_sensors) + str(start_time) + str(end_time))
    else:
        my_sensor_loc = request.form.getlist('sensor_locs')
        my_controller_loc = request.form.getlist('controller_locs')
        sensor_info, controller_info = assign_random(app_id, my_sensor_loc[0], my_controller_loc[0])
        logging.info("User selected data: " + str(app_id) + str(sensor_info) + str(start_time) + str(end_time))

    
    start_time = format_time(start_time)
    end_time = format_time(end_time)
    delta,time_to_execute = sh.get_scheduled_time(start_time)
    if(delta=="Invalid time"):
        error_msg = "Invalid Time"
        return render_template("error.html", error_msg=error_msg)
    if end_time < start_time:
        error_msg = "End time is less than start time"
        return render_template("error.html", error_msg=error_msg)
    
    # if option_selected == 'specific':
    #     sensor_info = {}
    #     for s in my_sensors:
    #         s_type, loc, s_id = s.split("-")
    #         if s_type not in sensor_info.keys():
    #             sensor_info[s_type] = [s_id]
    #         else:
    #             sensor_info[s_type].append(s_id)

    # req_func = []
    # for app_dict in app_data:
    #     if(app_id == app_dict["ApplicationID"]):
    #         app_name = app_dict["ApplicationName"]
    #         req_func = app_dict["Contract"]["sensors"]
    #         break
    

    # func_of_sensors = {}
    # for sensor in req_func:
    #     type_of_sensor = sensor["sensor_type"]
    #     if(type_of_sensor in func_of_sensors):
    #         func_of_sensors[type_of_sensor].append(sensor["function"])
    #     else:
    #         func_of_sensors[type_of_sensor] = []
    #         func_of_sensors[type_of_sensor].append(sensor["function"])
    # sensor_to_func_mapping =[]
    # for sensor_type,funcs in func_of_sensors.items():      
    #     for i in range(len(funcs)):
    #         d = {}
    #         if(len(sensor_info[sensor_type]) == len(func_of_sensors[sensor_type])):
    #             d["sensor_id"] = sensor_info[sensor_type][i]
    #             d["function"] = funcs[i]
    #             sensor_to_func_mapping.append(d)
    #         else:
    #             error_msg = "select required number of sensors"
    #             return render_template("error.html", error_msg=error_msg)
    sensor_to_func_mapping = []
    if option_selected == 'specific':
        sensor_info = {}
        for s in my_sensors:
            fun, loc, s_id = s.split("-")
            d = {}
            d["sensor_id"] = s_id
            d["function"] = fun
            sensor_to_func_mapping.append(d)


    print(sensor_to_func_mapping)
    print("//////////")

    """Controller to function mapping"""
    if option_selected == 'specific':
        controller_info = {}
        for s in my_controllers:
            s_type, loc, s_id = s.split("-")
            if s_type not in controller_info.keys():
                controller_info[s_type] = [s_id]
            else:
                controller_info[s_type].append(s_id)

    app_controller_data = []
    for app_dict in app_data:
        if(app_id == app_dict["ApplicationID"]):
            app_name = app_dict["ApplicationName"]
            app_controller_data = app_dict["Contract"]["controllers"]
            break
    

    func_of_controllers = {}
    for controller in app_controller_data:
        type_of_controller = controller["controller_type"]
        if(type_of_controller in func_of_controllers):
            func_of_controllers[type_of_controller].append(controller)
        else:
            func_of_controllers[type_of_controller] = []
            func_of_controllers[type_of_controller].append(controller)
    controller_to_func_mapping =[]
    for controller_type,data in func_of_controllers.items():      
        for i in range(len(data)):
            if(len(controller_info[controller_type]) == len(func_of_controllers[controller_type])): 
                data[i]["controller_id"] = controller_info[controller_type][i]
                controller_to_func_mapping.append(data[i])
            else:
                error_msg = "select required number of controllers"
                return render_template("error.html", error_msg=error_msg)

    logging.info("Sending data to deployer: " + str(app_id) + str(sensor_info))
    sched_id = insert_into_db(app_id, app_name, sensor_to_func_mapping, controller_to_func_mapping, start_time, end_time)
    query = {
        "ApplicationID":app_id,
        "app_name":app_name,
        "sensor_ids":sensor_to_func_mapping,
        "sched_id":sched_id,
        "controller_ids": controller_to_func_mapping,
        "type" : "app"
    }
    print(query)
    msg = sh.schedule_a_task(start_time, end_time, query=query)
    print(msg)
    return render_template ("deploy.html", time = start_time)


def get_app_specific_data(app_id):
    data = refresh_data()
    app_data = data["app"]
    sensor_data = data["sensor"]
    controller_data = data["controller"]
    list_of_sensors = [[sensor["sensor_id"],sensor['sensor_type'],sensor['sensor_location']] for sensor in sensor_data]
    list_of_controllers = [[controller["controller_id"],controller['controller_type'],controller['controller_location']] for controller in controller_data]

    req_sensors = []
    for app in app_data:
        if(app["ApplicationID"] == app_id):
            req_sensors = app["Contract"]["sensors"]

    sensors_of_app = {}
    for sensor in req_sensors:
        type_of_sensor = sensor["sensor_type"]
        func = sensor["function"]
        sens = []
        for sensor in list_of_sensors:
            if sensor[1] == type_of_sensor:
                sens.append([sensor[0],sensor[1],sensor[2]])
        sensors_of_app[func] = sens
    sensors_of_app_send = []
    for k,v in sensors_of_app.items():
        d={}
        d["sensor_type"] = k
        d["count"] = 1
        d["sensors_list"] = v
        sensors_of_app_send.append(d)
    print(sensors_of_app_send)
    
    # sensors_of_app = {}
    # for sensor in req_sensors:
    #     type_of_sensor = sensor["sensor_type"]
    #     if(type_of_sensor in sensors_of_app):
    #         sensors_of_app[type_of_sensor][0] +=1
    #     else:
    #         sensors_list = []
    #         for type in list_of_sensors:
    #             if(type[1] == type_of_sensor):
    #                 sensors_list.append([type[0],type[2]])

    #         sensors_of_app[type_of_sensor] = [1,[]]
    #         sensors_of_app[type_of_sensor][1] = sensors_list

    # sensors_of_app_send =[]
    # for k,v in sensors_of_app.items():
    #     d={}
    #     d["sensor_type"] = k
    #     d["sensors_list"] = v[1]
    #     d["count"] = v[0]
    #     sensors_of_app_send.append(d)



    req_controllers = []
    for app in app_data:
        if(app["ApplicationID"] == app_id):
            req_controllers = app["Contract"]["controllers"]
    

    controllers_of_app = {}
    for controller in req_controllers:
        type_of_controller = controller["controller_type"]
        if(type_of_controller in controllers_of_app):
            controllers_of_app[type_of_controller][0] +=1
        else:

            controllers_list = []
            for type in list_of_controllers:
                if(type[1] == type_of_controller):
                    controllers_list.append([type[0],type[2]])

            controllers_of_app[type_of_controller] = [1,[]]
            controllers_of_app[type_of_controller][1] = controllers_list

    controllers_of_app_send =[]
    for k,v in controllers_of_app.items():
        d={}
        d["controller_type"] = k
        d["controllers_list"] = v[1]
        d["count"] = v[0]
        controllers_of_app_send.append(d)

    data_to_send = {}
    data_to_send['sensor'] = sensors_of_app_send
    data_to_send['controller'] = controllers_of_app_send
    return data_to_send

@app.route('/get_app_contract',methods = ["POST"])  
def get_app_contract():
    app_id = json.loads(request.get_data())["app_id"]
    data_to_send = get_app_specific_data(app_id)
    return json.dumps(data_to_send)

def get_data_by_loc(app_id, spec_data, app_spec_data, data_type):
    data_by_loc = {}
    for data in spec_data:
        if data[data_type + "_location"] in data_by_loc:
            if data[data_type + "_type"] in data_by_loc[data[data_type + "_location"]]:
                data_by_loc[data[data_type + "_location"]][data[data_type + "_type"]].append(data[data_type + "_id"])
            else:
                data_by_loc[data[data_type + "_location"]][data[data_type + "_type"]] = []
                data_by_loc[data[data_type + "_location"]][data[data_type + "_type"]].append(data[data_type + "_id"])
        else:
            data_by_loc[data[data_type + "_location"]] = {}
            data_by_loc[data[data_type + "_location"]][data[data_type + "_type"]] = []
            data_by_loc[data[data_type + "_location"]][data[data_type + "_type"]].append(data[data_type + "_id"])

    db.temp_data.insert_one({"app_id":app_id, "type": data_type, "data": data_by_loc})
    loc_details = []
    for spec in app_spec_data:
        for loc, details in data_by_loc.items():
            if spec[data_type+"_type"] in data_by_loc[loc] and spec["count"] <= len(details[spec[data_type+"_type"]]):
                if loc not in loc_details:
                    loc_details.append(loc)
    return loc_details
    


@app.route('/get_locations', methods = ["POST"])
def get_locations():
    app_id = json.loads(request.get_data())["app_id"]
    data = refresh_data()
    app_data = data["app"]
    sensor_data = data["sensor"]
    controller_data = data["controller"]

    app_spec_data = {}
    cur_app = {}
    for app in app_data:
        if app["ApplicationID"] == app_id:
            cur_app = app
    temp_data = {}
    for sensor in cur_app["Contract"]["sensors"]:
        if sensor["sensor_type"] not in temp_data:
            temp_data[sensor["sensor_type"]] = 1
        else:
            temp_data[sensor["sensor_type"]] += 1
    sens_data = []
    for key, value in temp_data.items():
        sens_data.append({"sensor_type":key, "count":value})
    app_spec_data["sensor"] = sens_data

    temp_data = {}
    for sensor in cur_app["Contract"]["controllers"]:
        if sensor["controller_type"] not in temp_data:
            temp_data[sensor["controller_type"]] = 1
        else:
            temp_data[sensor["controller_type"]] += 1
    sens_data = []
    for key, value in temp_data.items():
        sens_data.append({"controller_type":key, "count":value})
    app_spec_data["controller"] = sens_data
    db.app_spec_data.insert_one({"app_id":app_id, "data":app_spec_data})

    sensor_locs = get_data_by_loc(app_id, sensor_data, app_spec_data["sensor"], "sensor")
    controller_locs = get_data_by_loc(app_id, controller_data, app_spec_data["controller"], "controller")
    loc_details = {}
    loc_details["sensor_locs"] = sensor_locs
    loc_details["controller_locs"] = controller_locs
    return json.dumps(loc_details)

def schedule_pending_tasks():
    pending_tasks = db.scheduleinfo.find({"instance_id":"blank"})
    for task in pending_tasks:
        query = {
            "ApplicationID":task["Application_ID"],
            "app_name":task["app_name"],
            "sensor_ids":task["sensor_info"],
            "controller_ids": task["controller_info"],
            "sched_id":task["sched_id"],
            "type":"app"
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
                query["type"] = "stop"
                msg = sh.schedule_a_stop_task(end_time, query=query)


def start():
    t = threading.Thread(target=sh.run_schedule)
    t.daemon = True
    t.start()
    pending_jobs = threading.Thread(target = schedule_pending_tasks)
    pending_jobs.start()
    db_watch_thread = threading.Thread(target=sh.db_change_detector, args=())
    db_watch_thread.start()
    app.run(debug = False, port = 8210, host='0.0.0.0')