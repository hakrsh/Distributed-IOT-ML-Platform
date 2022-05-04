import json
import sys

server_list = sys.argv[1]
servers = json.loads(open(server_list).read())

hostinfo = open('hostinfo.txt', 'w')

stub = """
#!/bin/sh

set -o errexit
set -o nounset

mkdir -p ~/.ssh
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -q -N '' -t rsa -f ~/.ssh/id_rsa
fi

"""
stub += "sshpass -p " + servers['master']['passwd'] + " ssh-copy-id -o StrictHostKeyChecking=no " + servers['master']['user'] + "@" + servers['master']['ip'] + "\n"
hostinfo.write(f"{servers['master']['user']}@{servers['master']['ip'] + '\n'}")

for worker in servers['workers']:
    stub += "sshpass -p " + worker['passwd'] + " ssh-copy-id -o StrictHostKeyChecking=no " + worker['user'] + "@" + worker['ip'] + "\n"
    hostinfo.write(f"{worker['user']}@{worker['ip'] + '\n'}")

with open('make_passwdless.sh', 'w') as f:
    f.write(stub)
hostinfo.close()
