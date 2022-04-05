#!/bin/bash
mkdir -p ~/.ssh
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -q -t rsa -N '' -f ~/.ssh/id_rsa <<<y >/dev/null 2>&1
fi
sudo apt -qq install sshpass jq -y
sudo pip3 install docker paramiko --quite

echo "Reading server list..."
master=`python3 read_json_master.py`
workers=`python3 read_json_workers.py`
IFS=',' ;
worker_ips=""
for i in $workers ; 
do 
    holder=$(echo $i | sed s/~/\\n/g)
    user=`echo "${holder}" | head -1`
    pass=`echo "${holder}"| head -2 | tail -1`
    worker_holder=$(echo $user | sed s/@/\\n/g)
    worker_ip=`echo "${worker_holder}"| head -2 | tail -1`
    worker_ips=$worker_ip","$worker_ips
    
    sshpass -p $pass ssh -o 'StrictHostKeyChecking no' $user "mkdir -p .ssh"
    cat ~/.ssh/id_rsa.pub | sshpass -p $pass ssh $user  'cat >> .ssh/authorized_keys'
    echo "installing docker on $worker_ip"
    scp install-docker.sh $user:~/
    ssh $user 'chmod +x install-docker.sh'
    ssh $user './install-docker.sh'
done
# For Master
holder=$(echo $master | sed s/~/\\n/g)
user=`echo "${holder}" | head -1`
pass=`echo "${holder}"| head -2 | tail -1`
master_holder=$(echo $user | sed s/@/\\n/g)
master_ip=`echo "${master_holder}"| head -2 | tail -1`

echo "making master passwordless"
sshpass -p $pass ssh -o 'StrictHostKeyChecking no' $user "mkdir -p .ssh"
cat ~/.ssh/id_rsa.pub | sshpass -p $pass ssh $user  'cat >> .ssh/authorized_keys'
ssh $user 'sudo apt-get -qq update'
ssh $user 'sudo apt-get -qq install python3 default-jre haproxy python3-pip -y'
ssh $user 'pip3 install docker --quite'
echo "installing docker on master"
scp install-docker.sh $user:~/
ssh $user 'chmod +x install-docker.sh'
ssh $user './install-docker.sh'

# Installing kafka
# add check wheteher file exists or not (no need to download it again).
ssh $user 'wget https://dlcdn.apache.org/kafka/3.1.0/kafka_2.13-3.1.0.tgz'
ssh $user 'tar -xzf kafka_2.13-3.1.0.tgz'
ssh $user 'rm kafka_2.13-3.1.0.tgz'
echo "Configuring kafka"
ssh $user "echo 'advertised.listeners=PLAINTEXT://'$master_ip':9092' >> ~/kafka_2.13-3.1.0/config/server.properties"
ssh $user "echo 'listeners=PLAINTEXT://0.0.0.0:9092' >> ~/kafka_2.13-3.1.0/config/server.properties"

# #######################Run at end#########################
# # Run zookeeper for kafka (background)
ssh $user 'nohup kafka_2.13-3.1.0/bin/zookeeper-server-start.sh config/zookeeper.properties &'
# # Run kafka (In Another Terminal)
ssh $user 'nohup kafka_2.13-3.1.0/bin/kafka-server-start.sh config/server.properties &'
echo "Zookeeper and kafka started"
# #######################Run at end#########################

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
    #make sure that $i is not void
    ssh $user "echo '  server server$count $i:9898 check'>>/etc/haproxy/haproxy.cfg"
    count=1+$count
done
ssh $user 'sudo chmod 644 /etc/haproxy/haproxy.cfg'
ssh $user 'touch "install_sucess"'
ssh $user 'line="@reboot sleep 60 && /home/"$(whoami)"/start_script.sh";(crontab -u $(whoami) -l; echo "$line" ) | sudo crontab -u $(whoami) -'
ssh $user 'wget https://gist.githubusercontent.com/nitin-kumar-iiith/e6b034c78690a37327e49d92381777c3/raw/fe56a6c8b21735d17b3702393f7948dd2ff8b23e/start_script.sh'
ssh $user 'chmod +x start_script.sh'
ssh $user './start_script.sh'

echo "!!!!!!!!!!!!!!!!BUILD STARTED!!!!!!!!!!!!!!!!!!!!1"
cd ../bootstrap
python3 build.py