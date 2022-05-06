#!/bin/bash

curl -fsSL https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt update
sudo apt --yes --no-install-recommends install mongodb-org

BIND_IP=0.0.0.0
echo "Configuring the mongod.conf file to update bindip and enable authentication"
sudo sed -i[bindIp] "s/bindIp: /bindIp: $BIND_IP #/g" /etc/mongod.conf 

sudo systemctl enable mongod
sudo systemctl start mongod.service