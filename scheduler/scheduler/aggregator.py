from kafka import KafkaConsumer, KafkaProducer


import json
import threading
import time
import pymongo


log_threads = dict()


def consume_log(topic,node_ip,node_port):
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers='{}:{}'.format(node_ip,node_port),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id="consumer-group-a"
        )
        
        print(consumer)
        print("Starting the consumer")
        for msg in consumer:
            # print("Registered User ={}".format(json.loads(msg.value)))
            print(msg.value)
            file_name = topic + ".txt"
            with open(file_name, "a") as f:
                f.write(msg.value.decode('utf-8') + '\n')
            # time.sleep(1)
            # break
    except Exception as e:
        print(e)
        # Kill the current thread
        # threading.Thread.join()





def get_instance_data_from_db():
    # mongoclient = MongoClient("mongodb+srv://root:root@ias.tu9ec.mongodb.net/repo?retryWrites=true&w=majority")
    # mongoclient = pymongo.MongoClient("mongodb://localhost:27017/")
    # db = mongoclient['instances_DB']
    # collection = db['inventory']
    # cursor = collection.find({})

    cursor=[{'topic':'logTopic2','ip':'localhost','port':'9092'}]

    for item in cursor:
        topic = item['topic']
        node_ip = item['ip']
        node_port = item['port']
        t = threading.Thread(target=consume_log,args=(topic,node_ip,node_port))
        # t.daemon = True
        log_threads[topic] = t
        t.start()


def get_instance_status_from_db():
    # mongoclient = MongoClient("mongodb+srv://root:root@ias.tu9ec.mongodb.net/repo?retryWrites=true&w=majority")
    # mongoclient = pymongo.MongoClient("mongodb://localhost:27017/")
    # db = mongoclient['instances_DB']
    # collection = db['inventory']
    # cursor = collection.find({})

    cursor=[{'topic':'logTopic2','ip':'localhost','port':'9092'}]

    for item in cursor:
        topic = item['topic']
        node_ip = item['ip']
        node_port = item['port']
        t = threading.Thread(target=consume_log,args=(topic,node_ip,node_port))
        # t.daemon = True
        log_threads[topic] = t
        t.start()


def new_instance_added(new_instance):
    topic = item['topic']
    node_ip = item['ip']
    node_port = item['port']
    t = threading.Thread(target=consume_log,args=(topic,node_ip,node_port))
    # t.daemon = True
    log_threads[topic] = t
    t.start()

def instance_deleted(instance):
    topic = instance['topic']
    log_threads[topic].join()
    log_threads.pop(topic)


# get_instance_data_from_db()
# t = threading.Thread(target=get_instance_data_from_db)
# t.daemon = True
# t.start()

get_instance_data_from_db()
get_instance_status_from_db()





    