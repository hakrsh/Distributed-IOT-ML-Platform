FROM python:3
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN ls /usr/share/zoneinfo && \
cp /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
ADD sensor_request_handler sensor_request_handler
CMD ["python", "-m","sensor_request_handler"]