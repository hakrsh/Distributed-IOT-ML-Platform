# communication library using kafka
import json
import threading
from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

class KafkaAdmin:
    admin_client = None
    bootstrap_servers = None
    topic_list = []
    def __init__(self, bootstrap_servers, client_id):
        self.bootstrap_servers = bootstrap_servers
        self.admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers, 
            client_id=client_id
        )
        self.topic_list = []

    # def create_topic(self, name, num_partitions=1, replication_factor=1):
    #     existing_topics = self.admin_client.list_topics()
    #     if name not in existing_topics:
    #         self.topic_list.append(NewTopic(name=name, num_partitions=num_partitions, replication_factor=replication_factor))
    #         self.admin_client.create_topics(new_topics=self.topic_list, validate_only=False)

    # def delete_topic(self, name):
    #     self.admin_client.delete_topics(topics=[name])
    
    def send_message(self, topic, message):
        producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers, value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send(topic, message)
        producer.close()
    
    def receive_message(self, topic, group_id, target_function,auto_offset_reset='earliest'):
        consumer = KafkaConsumer(topic, bootstrap_servers=self.bootstrap_servers, group_id=group_id, auto_offset_reset=auto_offset_reset)
        for message in consumer:
            threading.Thread(target=target_function, args=(message.value,)).start()
        consumer.close()

