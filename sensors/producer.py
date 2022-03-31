from kafka import KafkaProducer
import json
import time
from data import get_passengers
producer = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda v: json.dumps(v).encode('utf-8'))

if __name__ == '__main__':
    while True:
        user = get_passengers('test.csv')
        print(user)
        producer.send('users', user)
        time.sleep(1)
