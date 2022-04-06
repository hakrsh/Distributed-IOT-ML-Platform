import json
import logging

logging.basicConfig(level=logging.INFO)

with open("./servers.json", "r") as jsonfile:
    data = json.load(jsonfile)
    logging.info("Read successful")

master_username = data["master"]["user"]
master_ip = data["master"]["ip"]
master_password = data["master"]["pass"]
print(master_username+"@"+master_ip+"~"+master_password)
