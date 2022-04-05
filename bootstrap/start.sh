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
ssh $user 'sudo apt-get -qq install python3 default-jre haproxy python3-pip -y'
ssh $user 'pip3 install docker '
echo "installing docker on master"
scp install-docker.sh $user:~/
ssh $user 'chmod +x install-docker.sh'
ssh $user './install-docker.sh'

echo "Installing kafka on master"
scp install-kafka.sh $user:~/
ssh $user 'chmod +x install-kafka.sh'
ssh $user './install-kafka.sh'

echo "Configuring HAProxy"
ssh $user 'sudo chmod 777 /etc/haproxy/haproxy.cfg'
ssh $user 'echo "frontend deployer_service">>/etc/haproxy/haproxy.cfg'
ssh $user 'echo "  bind 127.0.0.1:9898">>/etc/haproxy/haproxy.cfg'
ssh $user 'echo "  default_backend deployers">>/etc/haproxy/haproxy.cfg'
ssh $user 'echo "backend deployers">>/etc/haproxy/haproxy.cfg'
ssh $user 'echo "  balance roundrobin">>/etc/haproxy/haproxy.cfg'

IFS=',' ;
count=2
for i in $worker_ips ; 
do
    ssh $user "echo '  server server$count $i:9898 check'>>/etc/haproxy/haproxy.cfg"
    count=1+$count
done
ssh $user 'sudo systemctl enable haproxy'
ssh $user 'sudo systemctl start haproxy'

echo "!!!!!!!!!!!!!!!!BUILD STARTED!!!!!!!!!!!!!!!!!!!!1"
python3 build.py
