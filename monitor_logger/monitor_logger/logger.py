from monitor_logger import kafka_server, module_config, db_instances, db_topics, client
import logging
import docker
from kafka import KafkaProducer
import threading

logging.basicConfig(filename="monitor_logger.log",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

producer = KafkaProducer(bootstrap_servers=[kafka_server],api_version=(0,10,1))
logging.info('Connected to kafka')


def push_to_kafka(instance_logs, instance_status, topic_id):
    try:
        producer.send(topic_id + "-status", instance_status)
        logging.info("Pushed status to topic")
        producer.send(topic_id + "-logs", instance_logs)
        logging.info("Pushed logs to topic")
    except Exception as e:
        logging.error(e)


def get_logs():
    try:
        # client = docker.from_env()
        ip = module_config["workers"][0]["ip"]
        name = module_config["workers"][0]["name"]
        print(ip, name)
        # client = docker.DockerClient(base_url="ssh://{}@{}".format(name, ip))
        logging.info("Connecting to VM")
        instances = db.instances.find({"ip":ip})
        logging.info("Getting instance details from db")
        instance_status = []
        instance_logs = []
        # containers = client.containers.list()
        # for cur_container in containers:
        #     instance_status.append({cur_container.id:cur_container.status})
        #     instance_logs.append({cur_container.id:cur_container.logs()})
        for instance in instances:
            cur_container = client.containers.get(instance["instance_id"])
            instance_status.append({cur_container.id:cur_container.status})
            instance_logs.append({cur_container.id:cur_container.logs()})
        cur_container = client.containers.get('f46cde6cf3')
        print(cur_container.logs())
        print(instance_status)
        print(instance_logs)
        push_to_kafka(instance_status, instance_logs, str(ip))
    
    except Exception as e:
        logging.error(e)

def delete_topics(instance_id):
    try:
        db.db_topics.remove({"topic_name":str(instance_id) + "-status"})
        db.db_topics.remove({"topic_name":str(instance_id) + "-logs"})
        logging.info("Removing topics")
    except Exception as e:
        logging.error(e)

def create_topics(instance_id):
    try:
        db.db_topics.insert_one({"topic_name":str(instance_id) + "-status"})
        db.db_topics.insert_one({"topic_name":str(instance_id) + "-logs"})
        logging.info("Inserting topics")
    except Exception as e:
        logging.error(e)

def db_watcher():
    print("Thread started")
    resume_token = None
    pipeline = [{'$match': { '$or': [ { 'operationType': 'insert' }, { 'operationType': 'delete' } ] }}]
    change_stream = client.scheduler.scheduleinfo.watch(pipeline)
    for change in change_stream:
        # print("change: ", change)
        if change["operationType"] == "insert":
            print(change["fullDocument"]["instance_id"])
        else:
            print(change["fullDocument"]["instance_id"])
            delete_topics(instance_id)
        resume_token = change_stream.resume_token

def start():
    logging.info("Logger started running")
    watcher = threading.Thread(target = db_watcher)
    watcher.start()
    # get_logs()