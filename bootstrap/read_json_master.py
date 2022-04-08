import json
import logging
import sys

logging.basicConfig(level=logging.INFO)
server_list = sys.argv[1]
with open(server_list, "r") as jsonfile:
    data = json.load(jsonfile)
    logging.info("Read successful")

master_username = data["master"]["user"]
master_ip = data["master"]["ip"]
master_password = data["master"]["pass"]
print(master_username+"@"+master_ip+"~"+master_password)
