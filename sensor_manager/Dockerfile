FROM python:3
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD sensor_manager sensor_manager
CMD ["python", "-m","sensor_manager"]
