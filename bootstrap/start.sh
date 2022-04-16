#!/bin/bash

set -o errexit
set -o nounset
export DEBIAN_FRONTEND=noninteractive

IFS=$(printf '\n\t')
SECONDS=0
mkdir -p ~/.ssh
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -q -N '' -t rsa -f ~/.ssh/id_rsa
fi
sudo apt -qq update && sudo apt -qq install python3 python3-pip sshpass jq -y > /dev/null
pip3 install docker paramiko jinja2 > /dev/null
echo "installed dependencies - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
read -p "Do you want to create new VMs? [y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 generate_bootstrap_config.py
    read -p "Do you want to install azure cli? [y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "installing azure cli..."
        curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash > /dev/null
        echo "Installed az-cli - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
        echo "Installing azure cli python..."
        pip install azure-cli --upgrade > /dev/null
        echo "Installed azure cli python - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
    fi
        az login
        echo "Logged in to azure - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
        echo "Creating VMs..."
        python3 create_vms.py platform_config.json
        sleep 10
        echo "Created VMs - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
fi

echo "Reading server list..."
master=`python3 read_json_master.py platform_config.json`
workers=`python3 read_json_workers.py platform_config.json`
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
    echo "made $user password less - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
    sleep 1
    echo "installing docker on $worker_ip"
    scp install-docker.sh $user:~/
    ssh $user 'chmod +x install-docker.sh'
    ssh $user './install-docker.sh' > /dev/null
done
echo "Installed docker on workers - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
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
sshpass -p $pass ssh-copy-id -o StrictHostKeyChecking=no $user > /dev/null
echo "$user now has passwordless access"
sleep 1
echo "installing docker on $user"
ssh $user 'sudo apt-get -qq update' > /dev/null
ssh $user 'sudo apt-get -qq install python3 default-jre python3-pip sshpass -y' > /dev/null
ssh $user 'pip3 install docker ' > /dev/null
echo "installing docker on master"
scp install-docker.sh $user:~/
ssh $user 'chmod +x install-docker.sh'
ssh $user './install-docker.sh' > /dev/null
echo "Installed docker on master - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"

echo "Installing kafka on master"
scp install-kafka.sh $user:~/
ssh $user 'chmod +x install-kafka.sh'
ssh $user 'sudo ./install-kafka.sh' > /dev/null
echo "Installed kafka on master - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
# prompt user to chose load balancer
echo "Please choose a load balancer"
echo "1. HAProxy (Recommended!)"
echo "2. IAS Group_3 Load Balancer"
read -p "Enter your choice: " choice
load_balancer=""
if [ $choice -eq 1 ]; then
    load_balancer="haproxy"
    echo "Installing HAProxy"
    ssh $user 'sudo apt-get -qq install haproxy -y' > /dev/null
    python3 config_haproxy.py
    scp haproxy.cfg $user:~/
    ssh $user 'sudo mv haproxy.cfg /etc/haproxy/haproxy.cfg'
    rm haproxy.cfg
    ssh $user 'sudo systemctl enable haproxy.service'
    ssh $user 'sudo systemctl restart haproxy.service'
elif [ $choice -eq 2 ]; then
    load_balancer="ias"
else
    load_balancer="ias"
    echo "Invald choice. Defaulting to IAS Group_3 Load Balancer"
fi
echo "Installed load balancer - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
echo "making passwordless access to workers from master"
python3 copy_ssh.py platform_config.json
scp copy_ssh.sh $user:~/
rm copy_ssh.sh
ssh $user 'chmod +x copy_ssh.sh'
ssh $user './copy_ssh.sh' > /dev/null
echo "Made passwordless access to workers from master - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
scp platform_config.json $user:~/
scp services.json $user:~/
scp -r ~/.azure $user:~/
echo "!!!!!!!!!!!!!!!!BUILD STARTED!!!!!!!!!!!!!!!!!!!!"
python3 build.py $load_balancer
echo "Build completed - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
