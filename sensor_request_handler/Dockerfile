FROM python:3.8-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN cp /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
echo "Asia/Kolkata" >  /etc/timezone
ADD sensor_request_handler sensor_request_handler
CMD ["python", "-m","sensor_request_handler"]