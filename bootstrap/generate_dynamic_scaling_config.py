import json
import logging
from uuid import uuid4
logging.basicConfig(level=logging.INFO)

logging.info("Generating dynamic scaling config")

number_of_vms = int(input("Enter number of VMs: (1-2): "))
if number_of_vms < 1 or number_of_vms > 2:
    print("Invalid number of VMs")
    exit(1)

servers = json.loads(open('platform_config.json').read())
subscription_id = servers['subscription_id']
location = "northeurope"
mongo_server = servers['mongo_server']
password = "Hackathon@2022"

sub = input('Default subscription id is {}. Do you want to change it? (y/n): '.format(subscription_id))
if sub == 'y':
    subscription_id = input("Enter subscription id: ")
loc = input(f'Default location is {location} for vm creation Do you want to change it? (y/n): ')
if loc == 'y':
    location = input("Enter location: ")

passwd = input(f'Default password is {password} for vm creation Do you want to change it? (y/n): ')
if passwd == 'y':
    password = input("Enter password: ")
workers = []
for i in range(number_of_vms):
    worker = {
        "user": str(uuid4())[:8],
        "ip": "",
        "pass": password,
        "location": location,
    }
    workers.append(worker)

server = {
    "workers": workers,
    "subscription_id": subscription_id,
}
with(open("dynamic_servers.json", "w")) as f:
    json.dump(server, f)
logging.info("Bootstrap config generated")