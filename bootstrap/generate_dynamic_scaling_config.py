import json
from uuid import uuid4

number_of_vms = 1
# number_of_vms = int(input("Enter number of VMs: (2-4): "))
# if number_of_vms < 2 or number_of_vms > 4:
#     print("Invalid number of VMs")
#     exit(1)
platform_config = json.loads(open("platform_config.json").read())
subscription_id = platform_config["subscription_id"]
location = platform_config["location"]
mongo_server = platform_config["mongo_server"]
password = platform_config["password"]

# sub = input('Default subscription id is {}. Do you want to change it? (y/n): '.format(subscription_id))
# if sub == 'y':
#     subscription_id = input("Enter subscription id: ")
# loc = input(f'Default location is {location} for vm creation Do you want to change it? (y/n): ')
# if loc == 'y':
#     location = input("Enter location: ")
# mongo = input('Do you want to change mongo server? (y/n): ')
# if mongo == 'y':
#     mongo_server = input("Enter mongo server: ")
# passwd = input(f'Default password is {password} for vm creation Do you want to change it? (y/n): ')
# if passwd == 'y':
#     password = input("Enter password: ")

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
