import json
import logging

logging.basicConfig(level=logging.INFO)
logging.info('Reading config files')
servers = json.loads(open('servers.json').read())

stub = """
#!/bin/sh

set -o errexit
set -o nounset

mkdir -p ~/.ssh
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -q -N '' -t rsa -f ~/.ssh/id_rsa
fi

"""
for worker in servers['workers']:
    stub += "sshpass -p " + worker['pass'] + " ssh-copy-id -o StrictHostKeyChecking=no " + worker['user'] + "@" + worker['ip'] + "\n"

with open('copy_ssh.sh', 'w') as f:
    f.write(stub)
