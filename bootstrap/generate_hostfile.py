import json
import sys

server_list = sys.argv[1]
servers = json.loads(open(server_list).read())

hostinfo = open('hostinfo.txt', 'w')
hostinfo.write(f"{servers['master']['user']}@{servers['master']['ip']} ")
for worker in servers['workers']:
    hostinfo.write(f"{worker['user']}@{worker['ip']} ")
hostinfo.close()
