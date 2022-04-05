import json
import logging

logging.basicConfig(level=logging.INFO)

with open("./config.json", "r") as jsonfile:
    data = json.load(jsonfile)
    logging.info("Read successful")

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