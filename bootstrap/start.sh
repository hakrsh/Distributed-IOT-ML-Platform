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
echo "installing dependencies..." > bootstrap.log
sudo apt -qq update && sudo apt -qq install python3 python3-pip sshpass jq -y >> bootstrap.log
pip3 install docker paramiko jinja2 >> bootstrap.log
echo "installed dependencies - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log
read -p "Do you want to rebuild the docker images? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 build_images.py
    echo "rebuilt docker images - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log
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
        echo "Installed az-cli - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log
        echo "Installing azure cli python..." >> bootstrap.log
        pip install azure-cli azure-identity --upgrade >> bootstrap.log
        echo "Installed azure cli python - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log
    fi
        az login
        echo "Logged in to azure - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log
        echo "Creating VMs..." >> bootstrap.log
        python3 create_vms.py platform_config.json
        sleep 10
        echo "Created VMs - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log
fi

echo "making Vms passwordless..." >> bootstrap.log
python3 make_vms_passwordless.py platform_config.json
bash make_passwdless.sh
echo "Vms passwordless - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log 
echo "Installing docker on workers..." >> bootstrap.log 
{
    read
    while read -p worker; do
        echo "installing docker on $worker" >> bootstrap.log
        scp install-docker.sh $worker:~/ 
        ssh $worker 'chmod +x install-docker.sh'
        ssh $worker './install-docker.sh' >> bootstrap.log
    done < hostinfo.txt
}
echo "Installed docker on workers - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log

master=`$(head -n 1 hostinfo.txt)`
echo "installing docker on $master"
ssh $master 'sudo apt-get -qq update' >> bootstrap.log
ssh $master 'sudo apt-get -qq install python3 python3-pip sshpass -y' >> bootstrap.log
ssh $master 'pip3 install docker ' >> bootstrap.log
echo "installing docker on master" >> bootstrap.log
scp install-docker.sh $master:~/ 
ssh $master 'bash install-docker.sh' >> bootstrap.log
echo "Installed docker on master - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"

echo "Installing kafka on master"
scp install-kafka.sh $master:~/ 
ssh $master 'sudo bash install-kafka.sh' >> bootstrap.log
echo "Installed kafka on master - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"
echo "Installing HAProxy" >> bootstrap.log
ssh $master 'sudo apt-get -qq install haproxy -y' >> bootstrap.log
python3 config_haproxy.py
scp haproxy.cfg $master:~/ >> bootstrap.log
ssh $master 'sudo mv haproxy.cfg /etc/haproxy/haproxy.cfg'
ssh $master 'sudo systemctl enable haproxy.service'
ssh $master 'sudo systemctl restart haproxy.service'
echo "Please choose a load balancer"
echo "1. HAProxy (Recommended!)"
echo "2. IAS Group_3 Load Balancer"
read -p "Enter your choice: " choice
load_balancer=""
if [ $choice -eq 1 ]; then
    load_balancer="haproxy"
elif [ $choice -eq 2 ]; then
    load_balancer="ias"
else
    load_balancer="haproxy"
    echo "Invald choice. Defaulting to HAProxy" >> bootstrap.log
fi

echo "making passwordless access to workers from master" >> bootstrap.log
python3 copy_ssh.py platform_config.json
scp ssh.sh $master:~/ 
ssh $master 'bash ssh.sh' >> bootstrap.log
echo "Made passwordless access to workers from master - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log
echo "Copying platform_config.json services.json and azure tokens to master" >> bootstrap.log
scp platform_config.json $master:~/ 
scp services.json $master:~/ 
scp -r ~/.azure $master:~/ 
echo "!!!!!!!!!!!!!!!!BUILD STARTED!!!!!!!!!!!!!!!!!!!!" >> bootstrap.log
python3 build.py $load_balancer
echo "Build completed - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log
