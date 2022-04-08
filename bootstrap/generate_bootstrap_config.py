import json
import logging
from uuid import uuid4
logging.basicConfig(level=logging.INFO)

logging.info("Generating bootstrap config")
number_of_vms = int(input("Enter number of VMs: (2-4): "))
if number_of_vms < 2 or number_of_vms > 4:
    print("Invalid number of VMs")
    exit(1)

subscription_id = "33f4f7cd-44fe-4cbe-b482-a5bce2fe048b"
location = "northeurope"
mongo_server = "mongodb+srv://root:root@ias.tu9ec.mongodb.net/repo?retryWrites=true&w=majority"
password = "Hackathon@2022"

sub = input('Default subscription id is {}. Do you want to change it? (y/n): '.format(subscription_id))
if sub == 'y':
    subscription_id = input("Enter subscription id: ")
loc = input(f'Default location is {location} for vm creation Do you want to change it? (y/n): ')
if loc == 'y':
    location = input("Enter location: ")
mongo = input('Do you want to change mongo server? (y/n): ')
if mongo == 'y':
    mongo_server = input("Enter mongo server: ")
passwd = input(f'Default password is {password} for vm creation Do you want to change it? (y/n): ')
if passwd == 'y':
    password = input("Enter password: ")
workers = []
for i in range(number_of_vms-1):
    worker = {
        "user": str(uuid4())[:8],
        "ip": "",
        "pass": password,
        "location": location,
    }
    workers.append(worker)

server = {
    "master": {
        "user": str(uuid4())[:8],
        "ip": "",
        "pass": password,
        "location": location
    },
    "workers": workers,
    "subscription_id": subscription_id,
    "mongo_server": mongo_server
}
with(open("servers.json", "w")) as f:
    json.dump(server, f)
logging.info("Bootstrap config generated")