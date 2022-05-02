#!/bin/bash

set -o errexit
set -o nounset

IFS=$(printf '\n\t')
echo "Dynamic scaling script started" > dynamic_scaling.log
echo "Generating keys..." >> dynamic_scaling.log
mkdir -p ~/.ssh
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -q -N '' -t rsa -f ~/.ssh/id_rsa
fi
cd platform_manager
echo "Generating server configs..." >> dynamic_scaling.log
python3 generate_dynamic_scaling_config.py
echo "Generating server configs... DONE" >> dynamic_scaling.log
echo "Creating vms..." >> dynamic_scaling.log
python3 create_vms.py dynamic_servers.json
echo "Creating vms... DONE" >> dynamic_scaling.log
sleep 10
echo "Starting vms..." >> dynamic_scaling.log
echo "Reading dynamic_server list..." >> dynamic_scaling.log
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
    sshpass -p $pass ssh-copy-id -o StrictHostKeyChecking=no $user >> dynamic_scaling.log
    echo "made $user password less"
    sleep 1
    echo "installing docker on $worker_ip"
    scp install-docker.sh $user:~/ >> dynamic_scaling.log
    ssh $user 'chmod +x install-docker.sh' 
    ssh $user './install-docker.sh' >> dynamic_scaling.log
done

# echo "making passwordless access to workers from master"
# master=`python3 read_json_master.py platform_config.json`
# holder=($(echo $master | sed s/~/\\n/g))
# user=`echo "${holder}" | head -1`
# echo $user
# python3 copy_ssh.py dynamic_servers.json
# scp copy_ssh.sh $user:~/ >> dynamic_scaling.log
# rm copy_ssh.sh
# ssh $user 'chmod +x copy_ssh.sh'
# ssh $user './copy_ssh.sh' >> dynamic_scaling.log
echo "!!!!!!!!!!!!!!!! DYNAMIC BUILD STARTED !!!!!!!!!!!!!!!!!!!!" >> dynamic_scaling.log
python3 dynamic_build.py
echo "!!!!!!!!!!!!!!!! DYNAMIC BUILD COMPLETED !!!!!!!!!!!!!!!!!!!!" >> dynamic_scaling.log
