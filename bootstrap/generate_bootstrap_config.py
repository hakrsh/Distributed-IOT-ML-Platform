import json
from uuid import uuid4

number_of_vms = int(input("Enter number of VMs: (2-4): "))
if number_of_vms < 2 or number_of_vms > 4:
    print("Invalid number of VMs")
    exit(1)

location = "northeurope"
mongo_server = "mongodb+srv://root:root@ias.tu9ec.mongodb.net/repo?retryWrites=true&w=majority"
password = "Hackathon@2022"
vm_size = "Standard_DS1_v2"

subscription_id = input("Enter subscription id: ")
loc = input(f'Default location is {location} for vm creation Do you want to change it? (y/n): ')
if loc == 'y':
    location = input("Enter location: ")
mongo = input('Do you want to change mongo server? (y/n): ')
if mongo == 'y':
    mongo_server = input("Enter mongo server: ")
passwd = input(f'Do you want to change the default password? (y/n): ')
if passwd == 'y':
    password = input("Enter password: ")
size = input(f'Do you want to change the default vm size ({vm_size})? (y/n): ')
if size == 'y':
    vm_size = input("Enter vm size: ")
workers = []
for i in range(number_of_vms-1):
    worker = {
        "user": 'w'+str(uuid4())[:4],
        "ip": "",
        "pass": password,
        "location": location,
    }
    workers.append(worker)

server = {
    "master": {
        "user": 'm'+str(uuid4())[:4],
        "ip": "",
        "pass": password,
        "location": location
    },
    "workers": workers,
    "subscription_id": subscription_id,
    "mongo_server": mongo_server,
    "vm_size": vm_size
}
with(open("platform_config.json", "w")) as f:
    json.dump(server, f)
