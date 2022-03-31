FROM python:3
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD sensor_request_handler sensor_request_handler
CMD ["python", "-m","sensor_request_handler"]