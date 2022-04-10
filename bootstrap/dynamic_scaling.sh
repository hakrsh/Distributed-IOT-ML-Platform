#!/bin/bash

set -o errexit
set -o nounset

IFS=$(printf '\n\t')

mkdir -p ~/.ssh
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -q -N '' -t rsa -f ~/.ssh/id_rsa
fi

# read -p "Do you want to create new VMs? [y/n] " -n 1 -r
# echo
# if [[ $REPLY =~ ^[Yy]$ ]]; then
#     read -p "Do you want to install azure cli? [y/n] " -n 1 -r
#     echo
#     python3 generate_dynamic_scaling_config.py
#     if [[ $REPLY =~ ^[Yy]$ ]]; then
#         echo "installing azure cli..."
#         curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash > /dev/null
#         echo "Installed az-cli"
#         echo "Installing azure cli python..."
#         pip install azure-cli --upgrade > /dev/null
#         echo "Installed azure cli python"
#     fi
#         az login
#         echo "Logged in to azure"
#         echo "Creating VMs..."
#         python3 create_vms.py dynamic_servers.json
# fi

read -p "Do you want to create new VMs? [y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating VMs..."
    python3 create_vms.py dynamic_servers.json
fi
echo "Reading dynamic_server list..."
workers=`python3 read_json_workers.py dynamic_servers.json`
IFS=',' ;
worker_ips=""
for i in $workers ; 
do 
    holder=($(echo $i | sed s/~/\\n/g))
    user=`echo "${holder}" | head -1`
    pass=`echo "${holder}"| head -2 | tail -1`
    worker_holder=($(echo $user | sed s/@/\\n/g))
    worker_ip=`echo "${worker_holder}"| head -2 | tail -1`
    worker_ips=$worker_ip","$worker_ips
    echo "making $user password less"
    # sudo -S sshpass -p $pass ssh -o 'StrictHostKeyChecking no' $user "mkdir -p .ssh"
    # cat ~/.ssh/id_rsa.pub | sudo sshpass -p $pass ssh $user  'cat >> .ssh/authorized_keys'
    sleep 2
    sshpass -p $pass ssh-copy-id -o StrictHostKeyChecking=no $user > /dev/null
    echo "made $user password less"
    sleep 1
    echo "installing docker on $worker_ip"
    scp install-docker.sh $user:~/ > /dev/null
    ssh $user 'chmod +x install-docker.sh' 
    ssh $user './install-docker.sh' > /dev/null
done

echo "making passwordless access to workers from master"
master=`python3 read_json_master.py platform_config.json`
holder=($(echo $master | sed s/~/\\n/g))
user=`echo "${holder}" | head -1`
echo $user
python3 copy_ssh.py dynamic_servers.json
scp copy_ssh.sh $user:~/ > /dev/null
rm copy_ssh.sh
ssh $user 'chmod +x copy_ssh.sh'
ssh $user './copy_ssh.sh' > /dev/null
echo "!!!!!!!!!!!!!!!! DYNAMIC BUILD STARTED !!!!!!!!!!!!!!!!!!!!"
python3 dynamic_build.py
echo "!!!!!!!!!!!!!!!! DYNAMIC BUILD COMPLETED !!!!!!!!!!!!!!!!!!!!"
