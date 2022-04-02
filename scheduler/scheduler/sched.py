import schedule
import time
import requests
import datetime
from scheduler import module_config

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
        print("Error at get_scheduled_time")


def update_instance_id(instance_id, sched_id):
    try:
        # logging.info("Updating instance IDs")
        db.scheduleinfo.update_one({"sched_id":sched_id},{"$set": {"instance_id": instance_id}})
    except Exception as e:
        print(e)


def end_app_instance(query):
    try:
        # Insert stopping Instance API Here
        response = requests.post(f"{module_config['deployer_master']}app",json=query).content
        print(response.decode('ascii'))
        print("FROM STOPPING INSTANCE!!!!")
        return schedule.CancelJob
    except Exception as e:
        print("Error at end_app_instance")


def schedule_a_stop_task(endtime,query):
    delta,time_to_execute = get_scheduled_time(endtime)

    schedule.every(delta.days + 1).days.at(time_to_execute).do(end_app_instance,query = query)
    return "Ending Instance Job scheduled"


def job_that_executes_once(query):
    """

    This function is executed at the specified time

    Usually the tasks are exceuted repeatedly at regular intervals. Therefore we are cancelling the job after first execution

    """
    print("Scheduling")
    try:
        print("Doing job....")
        # Use the Deployer API here
        response = requests.post(f"{module_config['deployer_master']}app",json=query).content
        instance_id = response.decode('ascii')
        update_instance_id(instance_id, query['sched_id'])

        end_time = datetime.datetime(2022, 4, 2, 12, 38)
        delta,time_to_execute = get_scheduled_time(end_time)
        if(delta=="Invalid time"):
            return "Invalid time"
        schedule.every(delta.days + 1).days.at(time_to_execute).do(end_app_instance,query = {"instance_id":instance_id})

        print(instance_id)
        return schedule.CancelJob

    except Exception as e:
        print(e)
        print("Error at job_that_executes_once")



# query = {
# "app_name":"App1",
# "location":"C:/Downloads",
# "topic_name":["Hospital","Factory"]
# }
def schedule_a_task(time,query):
    """

    We will check the validity of the time

    A job will be scheduled to happen at that time(i.e., a function call will take place at that time)

    """
    # time_to_execute = str(time.hour)+":"+str(time.minute)
    delta,time_to_execute = get_scheduled_time(time)

    schedule.every(delta.days + 1).days.at(time_to_execute).do(job_that_executes_once,query = query)
    return "job_scheduled"

# year = int(input("Enter year:"))
# month = int(input("Enter month:"))
# day = int(input("Enter day:"))
# hour = int(input("Enter hour:"))
# minute = int(input("Enter minute:"))
# schedule_time = datetime.datetime(year, month, day, hour, minute) 

# schedule_a_task(time = schedule_time,query = query)


def run_schedule():
    """

    This runs always and checks whether there are pending jobs to execute

    """
    while True:
        schedule.run_pending()
        time.sleep(1)