#!/bin/bash

set -o errexit
set -o nounset

IFS=$(printf '\n\t')

if [ ! -d /opt/kafka ]; then
    sudo apt update && sudo apt install -y default-jre
    curl https://dlcdn.apache.org/kafka/3.1.0/kafka_2.13-3.1.0.tgz | tar xz 
    mv kafka_2.13-3.1.0 /opt/kafka

    cat > /etc/systemd/system/kafka-zookeeper.service <<EOF
[Unit]
Description=Apache Zookeeper server (Kafka)
Documentation=http://zookeeper.apache.org
Requires=network.target remote-fs.target
After=network.target remote-fs.target

[Service]
Type=simple
User=$USER
Group=$USER
ExecStart=/opt/kafka/bin/zookeeper-server-start.sh /opt/kafka/config/zookeeper.properties
ExecStop=/opt/kafka/bin/zookeeper-server-stop.sh

[Install]
WantedBy=multi-user.target
EOF

    cat > /etc/systemd/system/kafka.service <<EOF
[Unit]
Description=Apache Kafka server (broker)
Documentation=http://kafka.apache.org/documentation.html
Requires=network.target remote-fs.target
After=network.target remote-fs.target kafka-zookeeper.service

[Service]
Type=simple
User=$USER
Group=$USER
ExecStart=/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
ExecStop=/opt/kafka/bin/kafka-server-stop.sh

[Install]
WantedBy=multi-user.target
EOF
    IFS=' '
    kafka_ip=($(hostname -I))
    # kafka_ip=$(curl -s http://whatismyip.akamai.com/)
    echo "advertised.listeners=PLAINTEXT://${kafka_ip}:9092" >> /opt/kafka/config/server.properties
    echo "listeners=PLAINTEXT://0.0.0.0:9092" >> /opt/kafka/config/server.properties
    
    systemctl daemon-reload
    systemctl enable kafka-zookeeper.service
    systemctl enable kafka.service
    systemctl start kafka-zookeeper.service
    sleep 5
    systemctl start kafka.service
    echo "Kafka is Running"
else
    echo "Kafka is already installed"
fi

