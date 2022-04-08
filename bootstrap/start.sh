#!/bin/sh

set -o errexit
set -o nounset

IFS=$(printf '\n\t')

mkdir -p ~/.ssh
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -q -N '' -t rsa -f ~/.ssh/id_rsa
fi
sudo apt -qq install sshpass jq -y
pip3 install docker paramiko jinja2 
echo "installed dependencies"

read -p "Do you want to create new VMs? [y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Do you want to install azure cli? [y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "installing azure cli..."
        curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
        echo "Installed az-cli"
        echo "Installing azure cli python..."
        pip install azure-cli
        echo "Installed azure cli python"
        az login
        echo "Logged in to azure"
        echo "Creating VMs..."
        python3 create_vms.py
    fi
fi
sleep 2
echo "Reading server list..."
master=`python3 read_json_master.py servers.json`
workers=`python3 read_json_workers.py servers.json`
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
    sshpass -p $pass ssh-copy-id -o StrictHostKeyChecking=no $user
    echo "made $user password less"
    sleep 1
    echo "installing docker on $worker_ip"
    scp install-docker.sh $user:~/
    ssh $user 'chmod +x install-docker.sh'
    ssh $user './install-docker.sh'
done
# For Master
holder=($(echo $master | sed s/~/\\n/g))
user=`echo "${holder}" | head -1`
pass=`echo "${holder}"| head -2 | tail -1`
master_holder=($(echo $user | sed s/@/\\n/g))
master_ip=`echo "${master_holder}"| head -2 | tail -1`

echo "making $user passwordless"
# sudo -S sshpass -p $pass ssh -o 'StrictHostKeyChecking no' $user "mkdir -p .ssh"
# cat ~/.ssh/id_rsa.pub | sudo sshpass -p $pass ssh $user  'cat >> .ssh/authorized_keys'
sleep 2
sshpass -p $pass ssh-copy-id -o StrictHostKeyChecking=no $user
echo "$user now has passwordless access"
sleep 1
echo "installing docker on $user"
ssh $user 'sudo apt-get -qq update'
ssh $user 'sudo apt-get -qq install python3 default-jre python3-pip sshpass -y'
ssh $user 'pip3 install docker '
echo "installing docker on master"
scp install-docker.sh $user:~/
ssh $user 'chmod +x install-docker.sh'
ssh $user './install-docker.sh'

echo "Installing kafka on master"
scp install-kafka.sh $user:~/
ssh $user 'chmod +x install-kafka.sh'
ssh $user 'sudo ./install-kafka.sh'
# prompt user to chose load balancer
echo "Please choose a load balancer"
echo "1. HAProxy"
echo "2. IAS Group 3 Load Balancer"
read -p "Enter your choice: " choice
load_balancer=""
if [ $choice -eq 1 ]; then
    load_balancer="haproxy"
    echo "Installing HAProxy"
    ssh $user 'sudo apt-get -qq install haproxy -y'
    python3 config_haproxy.py
    scp haproxy.cfg $user:~/
    ssh $user 'sudo mv haproxy.cfg /etc/haproxy/haproxy.cfg'
    rm haproxy.cfg
    ssh $user 'sudo systemctl enable haproxy.service'
    ssh $user 'sudo systemctl restart haproxy.service'
elif [ $choice -eq 2 ]; then
    load_balancer="ias"
    echo "Installing IAS Group 3 Load Balancer"
else
    echo "Invalid choice"
fi
echo "making passwordless access to workers from master"
python3 copy_ssh.py servers.json
scp copy_ssh.sh $user:~/
rm copy_ssh.sh
ssh $user 'chmod +x copy_ssh.sh'
ssh $user './copy_ssh.sh'
echo "!!!!!!!!!!!!!!!!BUILD STARTED!!!!!!!!!!!!!!!!!!!!"
python3 build.py $load_balancer
echo "!!!!!!!!!!!!!!!!BUILD COMPLETED!!!!!!!!!!!!!!!!!!!!"
