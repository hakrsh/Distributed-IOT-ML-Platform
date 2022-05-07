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
sudo apt update >> bootstrap.log
sudo apt install python3 python3-pip sshpass jq -y >> bootstrap.log
pip3 install docker paramiko jinja2 >> bootstrap.log
echo "installed dependencies - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log
read -p "Do you want to rebuild the docker images? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 build_images.py
    echo "rebuilt docker images - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log
fi
azure="false"
read -p "Do you want to create new VMs? [y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    azure="true"
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

# echo "Please choose a load balancer"
# echo "1. HAProxy (Recommended!)"
# echo "2. IAS Group_3 Load Balancer"
# read -p "Enter your choice: " choice
# if [ $choice -eq 1 ]; then
#     load_balancer="haproxy"
# elif [ $choice -eq 2 ]; then
#     load_balancer="ias"
# else
#     load_balancer="haproxy"
#     echo "Invald choice. Defaulting to HAProxy" >> bootstrap.log
# fi
load_balancer="haproxy"
echo "Using $load_balancer as the load balancer" >> bootstrap.log

echo "Preparing hostinfo.txt..." >> bootstrap.log
python3 generate_hostfile.py platform_config.json

echo "making Vms passwordless..." >> bootstrap.log
python3 make_passwdless_ssh.py platform_config.json
bash make_passwdless.sh
echo "Vms passwordless - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log 

declare -a VMS=$(cat hostinfo.txt)
IFS=' '
for host in $VMS ; do
    echo "adding cronjob to $host to clear ram cache..." >> bootstrap.log
    echo "$(echo '*/1 *    * * * sync && echo 3 | sudo tee /proc/sys/vm/drop_caches')"| ssh $host "crontab -"
    echo "added cronjob to $host" >> bootstrap.log
    echo "installing docker on $host" >> bootstrap.log
    scp install-docker.sh $host:~/ 
    scp restart_services.py $host:~/ # for manual restart
    ssh $host 'bash install-docker.sh' >> bootstrap.log
    ssh $host 'sudo apt-get install python3 python3-pip -y' >> bootstrap.log
    ssh $host 'pip3 install docker ' >> bootstrap.log
    echo "installed docker on $host - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log
    echo "Copying platform_config.json and services.json to $host" >> bootstrap.log
    scp platform_config.json $host:~/ 
    scp services.json $host:~/ 
done

master=($(cat hostinfo.txt))
echo "Installing kafka on master" >> bootstrap.log
scp install-kafka.sh $master:~/ 
ssh $master 'sudo bash install-kafka.sh' >> bootstrap.log
echo "Installed kafka on master - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log

echo "Installing mongodb on master" >> bootstrap.log
scp install-mongo.sh $master:~/
ssh $master 'sudo bash install-mongo.sh' >> bootstrap.log
echo "Installed mongodb on master - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log

echo "Installing HAProxy" >> bootstrap.log
ssh $master 'sudo apt-get install haproxy -y' >> bootstrap.log
python3 config_haproxy.py
scp haproxy.cfg $master:~/ >> bootstrap.log
ssh $master 'sudo mv haproxy.cfg /etc/haproxy/haproxy.cfg'
ssh $master 'sudo systemctl enable haproxy.service'
ssh $master 'sudo systemctl restart haproxy.service'

echo "making passwordless access to workers from master" >> bootstrap.log
ssh $master 'sudo apt-get install sshpass -y' >> bootstrap.log
python3 copy_ssh.py platform_config.json
scp ssh.sh $master:~/ 
ssh $master 'bash ssh.sh' >> bootstrap.log
echo "Made passwordless access to workers from master - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log

if [ $azure == "true" ]; then
    scp -r ~/.azure $master:~/ 
fi

echo "Deploying containers..." >> bootstrap.log
python3 deploy.py $load_balancer
tail -n 1 bootstrap.log
echo "Total time elapsed: $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> bootstrap.log