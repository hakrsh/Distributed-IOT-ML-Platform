from monitor_logger import kafka_server, module_config, db_instances, db_topics, client
import logging
import docker
from kafka import KafkaProducer
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
    try:

        print(producer)
        print("In producer function",topic_id)
        x= producer.send(topic_id + "-status", instance_status)
        print(x)
        logging.info("Pushed status to topic")
        print("Pushed status to topic")
        producer.send(topic_id + "-logs", instance_logs)
        logging.info("Pushed logs to topic")
    except Exception as e:
        print(e)
        print("errr")
        logging.error(e)
        


def get_instance_data(client,instance_id):
    print(client)
    cur_container = client.containers.get(instance_id)
    instance_status = {cur_container.id:cur_container.status}
    instance_logs = {cur_container.id:cur_container.logs()}
    print(instance_status, instance_logs)
    if not check_topic(instance_id):
        create_topics(instance_id)
    print("calling kafka")
    push_to_kafka(instance_status, instance_logs, instance_id)

def get_logs():
    try:
        client = docker.from_env()
        ip = module_config["workers"][0]["ip"]
        name = module_config["workers"][0]["name"]
        print(ip, name)
        # client = docker.DockerClient(base_url="ssh://{}@{}".format(name, ip))
        logging.info("Connecting to VM")
        # instances = db.instances.find({"ip":ip})
        logging.info("Getting instance details from db")
        thread_list = []
        instances = ["27d0d5a208e2", "fd93eaaa9698"]
        for instance in instances:
            print(instance)
            print(client)
            thread = threading.Thread(target=get_instance_data, args=(client,instance))
            thread_list.append(thread)
            thread.start()
            for thread in thread_list:
                thread.join()
    except Exception as e:
        logging.error(e)

def delete_topics(instance_id):
    try:
        db_topics.topics.remove({"topic_name":str(instance_id) + "-status"})
        db_topics.topics.remove({"topic_name":str(instance_id) + "-logs"})
        logging.info("Removing topics")
    except Exception as e:
        logging.error(e)

def create_topics(instance_id):
    try:
        db_topics.topics.insert_one({"topic_name":str(instance_id) + "-status"})
        db_topics.topics.insert_one({"topic_name":str(instance_id) + "-logs"})
        logging.info("Inserting topics")
    except Exception as e:
        logging.error(e)

def check_topic(topic_name):
    try:
        topic_count = db_topics.topics.find({"topic_name":str(topic_name) + "-status"})
        if len(list(topic_count)) == 0:
            return False
        else:
            return True
    except Exception as e:
        logging.error(e)

def db_watcher():
    print("Thread started")
    resume_token = None
    pipeline = [{'$match': { '$or': [ { 'operationType': 'insert' }, { 'operationType': 'delete' } ] }}]
    change_stream = client.scheduler.scheduleinfo.watch(pipeline)
    for change in change_stream:
        if change["operationType"] == "insert":
            print(change["fullDocument"]["instance_id"])
            thread = threading.Thread(target=get_instance_data, args=(client, change["fullDocument"]["instance_id"]))
        else:
            print(change["fullDocument"]["instance_id"])
            delete_topics(instance_id)
        resume_token = change_stream.resume_token

def start():
    logging.info("Logger started running")
    watcher = threading.Thread(target = db_watcher)
    watcher.start()
    get_logs()
    # scheduler = BlockingScheduler()
    # scheduler.add_job(get_logs, 'interval', seconds=module_config["frequency"])
    # try:
    #     scheduler.start()
    # except (KeyboardInterrupt, SystemExit):
    #     pass
    # finally:
    #     scheduler.shutdown()