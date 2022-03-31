import schedule
import time
import requests
import datetime
from scheduler import module_config

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
        print(response.decode('ascii'))
        return schedule.CancelJob
    except:
        print("error")



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
    time_to_execute = "{:02d}:{:02d}".format(time.hour,time.minute)
    print(time_to_execute)
    today = datetime.datetime.now()
    if(today>=time):
        return "Invalid time"
    delta = time - today
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