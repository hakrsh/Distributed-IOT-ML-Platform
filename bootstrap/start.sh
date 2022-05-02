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
echo "installing dependencies..."
sudo apt -qq update && sudo apt -qq install python3 python3-pip sshpass jq -y > bootstrap.log
pip3 install docker paramiko jinja2 >> bootstrap.log
echo "installed dependencies - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
read -p "Do you want to rebuild the docker images? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 build_images.py
    echo "rebuilt docker images - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
fi
read -p "Do you want to create new VMs? [y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 generate_bootstrap_config.py
    read -p "Do you want to install azure cli? [y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "installing azure cli..."
        curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash >> bootstrap.log
        echo "Installed az-cli - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
        echo "Installing azure cli python..."
        pip install azure-cli azure-identity --upgrade >> bootstrap.log
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
    sshpass -p $pass ssh-copy-id -o StrictHostKeyChecking=no $user >> bootstrap.log
    echo "made $user password less - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
    sleep 1
    echo "installing docker on $worker_ip"
    scp install-docker.sh $user:~/ >> bootstrap.log
    ssh $user 'chmod +x install-docker.sh'
    ssh $user './install-docker.sh' >> bootstrap.log
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
sshpass -p $pass ssh-copy-id -o StrictHostKeyChecking=no $user >> bootstrap.log
echo "$user now has passwordless access"
sleep 1
echo "installing docker on $user"
ssh $user 'sudo apt-get -qq update' >> bootstrap.log
ssh $user 'sudo apt-get -qq install python3 default-jre python3-pip sshpass -y' >> bootstrap.log
ssh $user 'pip3 install docker ' >> bootstrap.log
echo "installing docker on master"
scp install-docker.sh $user:~/ >> bootstrap.log
ssh $user 'chmod +x install-docker.sh'
ssh $user './install-docker.sh' >> bootstrap.log
echo "Installed docker on master - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"

echo "Installing kafka on master"
scp install-kafka.sh $user:~/ >> bootstrap.log
ssh $user 'chmod +x install-kafka.sh'
ssh $user 'sudo ./install-kafka.sh' >> bootstrap.log
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
    ssh $user 'sudo apt-get -qq install haproxy -y' >> bootstrap.log
    python3 config_haproxy.py
    scp haproxy.cfg $user:~/ >> bootstrap.log
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
scp copy_ssh.sh $user:~/ >> bootstrap.log
rm copy_ssh.sh
ssh $user 'chmod +x copy_ssh.sh' >> bootstrap.log
ssh $user './copy_ssh.sh' >> bootstrap.log
echo "Made passwordless access to workers from master - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
scp platform_config.json $user:~/ >> bootstrap.log
scp services.json $user:~/ >> bootstrap.log
scp -r ~/.azure $user:~/ >> bootstrap.log
echo "!!!!!!!!!!!!!!!!BUILD STARTED!!!!!!!!!!!!!!!!!!!!"
python3 build.py $load_balancer
echo "Build completed - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
