from monitor_logger import kafka_server, module_config, db
import logging
import docker
import threading
from apscheduler.schedulers.blocking import BlockingScheduler


logging.basicConfig(filename="monitor_logger.log",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

producer = KafkaProducer(bootstrap_servers=[kafka_server],api_version=(0,10,1))
logging.info('Connected to kafka')


def push_to_kafka(instance_logs, instance_status, topic_id):
    producer.send(topic_id + "-status", instance_status)
    producer.send(topic_id + "-logs", instance_logs)


def get_instance_data(client,instance_id):

    cur_container = client.containers.get(instance_id)
    instance_status = {cur_container.id:cur_container.status}
    instance_logs = {cur_container.id:cur_container.logs()}

    print(cur_container.logs())
    print(instance_status)
    print(instance_logs)
    push_to_kafka(instance_status, instance_logs, instance_id)

def get_logs():
    try:
        client = docker.from_env()
        ip = module_config["workers"][0]["ip"]
        instances = db.instances.find({"ip":ip})
        # instance_status = []
        # instance_logs = []
        # containers = client.containers.list()
        # for cur_container in containers:
        #     instance_status.append({cur_container.id:cur_container.status})
        #     instance_logs.append({cur_container.id:cur_container.logs()})
        # for instance in instances:
        #     cur_container = client.containers.get(instance["instance_id"])
        #     instance_status.append({cur_container.id:cur_container.status})
        #     instance_logs.append({cur_container.id:cur_container.logs()})
        # cur_container = client.containers.get('f46cde6cf3')


       
        thread_list = []
        for instance in instances:
            thread = threading.Thread(target=get_instance_data, args=(client,instance["instance_id"]))
            thread_list.append(thread)
            thread.start()
        for thread in thread_list:
            thread.join()


        # print(cur_container.logs())
        # print(instance_status)
        # print(instance_logs)
        # push_to_kafka(instance_status, instance_logs, str(ip))
        
        
    except Exception as e:
        print(e)

def start():


    scheduler = BlockingScheduler()
    scheduler.add_job(get_logs, 'interval', seconds=module_config["frequency"])
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        scheduler.shutdown()
