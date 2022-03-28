FROM python:3
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD sensors_req_handler sensors_req_handler
CMD ["python", "sensors_req_handler"]
