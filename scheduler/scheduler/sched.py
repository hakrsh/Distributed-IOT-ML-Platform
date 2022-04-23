import schedule
import time
import requests
import datetime
from scheduler import module_config, db, messenger
import logging
import json
from scheduler import db, client
from dateutil import parser
instance_db = client.repo

logging.basicConfig(        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)


def update_stopped_status(instance_id):
    try:
        logging.info("Updating stopped status")
        db.scheduleinfo.update_one({"instance_id":instance_id},{"$set": {"stopped_flag": True}})
    except Exception as e:
        logging.error(e)

def get_scheduled_time(time):
    try:
        # time_to_execute = str(time.hour)+":"+str(time.minute)
        time_to_execute = "{:02d}:{:02d}".format(time.hour,time.minute)
        print(time_to_execute)
        today = datetime.datetime.now()
        if(today>=time):
            return "Invalid time","None"
        delta = time - today
        return delta,time_to_execute
    except Exception as e:
        logging.error("Error at get_scheduled_time")
        logging.error(e)


def update_instance_id(instance_id, sched_id):
    try:
        logging.info("Updating instance IDs")
        db.scheduleinfo.update_one({"sched_id":sched_id},{"$set": {"instance_id": instance_id}})
    except Exception as e:
        logging.error(e)


def end_app_instance(query):
    try:
        response = requests.post(f"{module_config['deployer_master']}stop-instance",json=query).content
        print(response.decode('ascii'))
        print("FROM STOPPING INSTANCE!!!!")
        update_stopped_status(query["instance_id"])
        return schedule.CancelJob
    except Exception as e:
        logging.error("Error at end_app_instance")
        logging.error(e)


def schedule_a_stop_task(endtime,query):
    delta,time_to_execute = get_scheduled_time(endtime)
    if(delta=="Invalid time"):
            return "Invalid time"
    schedule.every(delta.days + 1).days.at(time_to_execute).do(end_app_instance,query = query)
    return "Ending Instance Job scheduled"


def call_deployer(query, end_time):
    """

    This function is executed at the specified time

    Usually the tasks are exceuted repeatedly at regular intervals. Therefore we are cancelling the job after first execution

    """
    print("Scheduling")
    try:
        print("Doing job....")
        messenger.send_message('to_deployer_master', query)
        logging.info("Wrote to kafka topic: to_deployer")
        # response = requests.post(f"{module_config['deployer_master']}app",json=query)
        # print(type(response.text))
        # print(type(json.loads(response.text)))
        # response = json.loads(response.text)
        # instance_id = response["InstanceID"]
        # print(instance_id)
        # update_instance_id(instance_id, query['sched_id'])
        # delta,time_to_execute = get_scheduled_time(end_time)
        # if(delta=="Invalid time"):
        #     return "Invalid time"
        # schedule.every(delta.days + 1).days.at(time_to_execute).do(end_app_instance,query = {"instance_id":instance_id})
        # print(instance_id)
        return schedule.CancelJob

    except Exception as e:
        logging.error("Error at call_deployer")
        logging.error(e)
        

def schedule_a_task(start_time, end_time, query):
    """

    We will check the validity of the time

    A job will be scheduled to happen at that time(i.e., a function call will take place at that time)

    """
    # time_to_execute = str(time.hour)+":"+str(time.minute)
    delta,time_to_execute = get_scheduled_time(start_time)
    if(delta=="Invalid time"):
        return "Invalid time"
    schedule.every(delta.days + 1).days.at(time_to_execute).do(call_deployer, query = query, end_time = end_time)
    return "job_scheduled"

def run_schedule():
    """

    This runs always and checks whether there are pending jobs to execute

    """
    while True:
        schedule.run_pending()
        time.sleep(1)

def db_change_detector():

    while len(list(instance_db.instances.find({'type': 'app'}))) == 0:
        continue

    first_row =  instance_db.instances.find_one({'type': 'app'})
    instance_id = first_row['instance_id']
    sched_id = first_row['sched_id']
    update_instance_id(instance_id, sched_id)
    end_time = parser.parse(first_row['end_time'])
    schedule_a_stop_task(end_time,query={"instance_id":instance_id})

    instance_collection = instance_db.instances
    for change in instance_collection.watch():
        change_type = change['operationType']
        if change_type == "insert" and change["fullDocument"]["type"]=="app":
            instance_id = change["fullDocument"]['instance_id']
            sched_id = change["fullDocument"]['sched_id']
            query = {'sched_id':sched_id}
            update_instance_id(instance_id, sched_id)
            end_time = parser.parse(change["fullDocument"]['end_time'])
            schedule_a_stop_task(end_time,query={"instance_id":instance_id})
            # db.scheduleinfo.update_one(query,{"$set": { "instance_id": instance_id }})
            # schedule.every(delta.days + 1).days.at(time_to_execute).do(end_app_instance,query = {"instance_id":instance_id})