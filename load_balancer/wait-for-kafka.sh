#!/usr/bin/env bash
kafka_ip=`cat $1/config.json | jq -r '.kafka_ip'`
echo "Waiting for kafka to start"
bash /wait-for-it.sh -t 60 ${kafka_ip}:9092 -s -- echo "Kafka is up" 
python3 -m $1