import json
import sys

server_list = sys.argv[1]

with open(server_list, "r") as jsonfile:
    data = json.load(jsonfile)

str = ""
first = True
for x in data["workers"]:
    if first:
        first = False
        # str = x["ip"]
        str = x["user"]+"@"+x["ip"]+'~'+x["pass"]
    else:
        str = str+","+x["user"]+"@"+x["ip"]+'~'+x["pass"]
print(str)
