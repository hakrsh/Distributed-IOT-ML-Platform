# IOT-ML-Platform
- Built a Distributed Platform that is capable of managing and running IoT-ML applications on it.
- The platform is able to register new sensors.
- API is provided for the application developer to get data from the respective sensor.
- The platform has features like scheduling, monitoring, notification, fault tolerance.
- Kafka cluster is setup to receive stream of sensor data and forward it to multiple algorithms subscribed for that sensor.
- All the services of the platform are containerized (running in docker)

### Requrements to run 
* multipass [https://multipass.run/]
* docker [https://docker.com/]

## How to deploy the platform
### Azure deployment
```
git clone https://github.com/harikn77/IOT-ML-Platform.git
cd IOT-ML-Platform/bootstrap
sudo bash start.sh
```
### Local deployment

1. Run the following command in the terminal:
```
git clone https://github.com/harikn77/IOT-ML-Platform.git
multipass launch -c 4 -m 2G -d 10G --name master
multipass launch -c 4 -d 10G --name worker1
multipass launch -c 4 -d 10G --name worker2
```
2. Set password for each machine:
```
multipass shell <name>
sudo passwd ubuntu
```
for example:
```
multipass shell master
sudo passwd ubuntu
```
3. Enable password based SSH on each machine:
```
multipass shell <name>
sudo vim /etc/ssh/sshd_config
Search for `PasswordAuthentication` and set the option to 'yes'.
sudo systemctl restart sshd
```
4. Update `platform_config.json`
5. Run the following command in the terminal:
```
cd IOT-ML-Platform/bootstrap
sudo bash start.sh
```
