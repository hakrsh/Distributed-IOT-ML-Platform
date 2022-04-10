import json
import sys

server_list = sys.argv[1]
with open(server_list, "r") as jsonfile:
    data = json.load(jsonfile)

master_username = data["master"]["user"]
master_ip = data["master"]["ip"]
master_password = data["master"]["pass"]
print(master_username+"@"+master_ip+"~"+master_password)
