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

echo "Preparing hostinfo.txt..." >> dynamic_scaling.log
python3 generate_hostfile.py dynamic_servers.json
echo "making Vms passwordless..." >> dynamic_scaling.log
python3 make_passwdless_ssh.py dynamic_servers.json
bash make_passwdless.sh

declare -a VMS=$(cat hostinfo.txt)
IFS=' '
for host in $VMS ; do
    echo "adding cronjob to $host to clear ram cache..." >> dynamic_scaling.log
    echo "$(echo '*/1 *    * * * sync && echo 3 | sudo tee /proc/sys/vm/drop_caches')"| ssh $host "crontab -"
    echo "added cronjob to $host" >> dynamic_scaling.log
    echo "installing docker on $host" >> dynamic_scaling.log
    scp install-docker.sh $host:~/ 
    ssh $host 'bash install-docker.sh' >> dynamic_scaling.log
    echo "installed docker on $host - $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds" >> dynamic_scaling.log
done

echo "Deploying containers..." >> dynamic_scaling.log
python3 dynamic_build.py
echo "Deploying containers... DONE" >> dynamic_scaling.log
