FROM python:3.8-slim
COPY requirements.txt .
COPY wait-for-it.sh .
COPY wait-for-kafka.sh .

RUN apt-get update && apt-get install -y jq

RUN pip install -r requirements.txt
RUN cp /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
echo "Asia/Kolkata" >  /etc/timezone
ADD deployer deployer
ENTRYPOINT ["/wait-for-kafka.sh", "deployer"]