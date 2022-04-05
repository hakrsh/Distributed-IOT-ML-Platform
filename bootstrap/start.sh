#!/bin/bash
mkdir -p ~/.ssh
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -q -N '' -t rsa -f ~/.ssh/id_rsa
fi
sudo apt -qq install sshpass jq -y
sudo pip3 install docker paramiko 

echo "Reading server list..."
master=`python3 read_json_master.py`
workers=`python3 read_json_workers.py`
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
    sshpass -p $pass ssh -o 'StrictHostKeyChecking no' $user "mkdir -p .ssh"
    cat ~/.ssh/id_rsa.pub | sshpass -p $pass ssh $user  'cat >> .ssh/authorized_keys'
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
sshpass -p $pass ssh -o 'StrictHostKeyChecking no' $user "mkdir -p .ssh"
cat ~/.ssh/id_rsa.pub | sshpass -p $pass ssh $user  'cat >> .ssh/authorized_keys'
ssh $user 'sudo apt-get -qq update'
ssh $user 'sudo apt-get -qq install python3 default-jre python3-pip -y'
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
if [ $choice -eq 1 ]; then
    echo "Installing HAProxy"
    ssh $user 'sudo apt-get -qq install haproxy -y'
    python3 config_haproxy.py
    scp haproxy.cfg $user:~/
    ssh $user 'sudo mv haproxy.cfg /etc/haproxy/haproxy.cfg'
    ssh $user 'sudo systemctl enable haproxy'
    ssh $user 'sudo systemctl start haproxy'
elif [ $choice -eq 2 ]; then
    echo "Installing IAS Group 3 Load Balancer"
else
    echo "Invalid choice"
fi

echo "!!!!!!!!!!!!!!!!BUILD STARTED!!!!!!!!!!!!!!!!!!!!1"
python3 build.py
