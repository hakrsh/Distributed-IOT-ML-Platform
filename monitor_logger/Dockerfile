FROM python:3
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN cp /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
echo "Asia/Kolkata" >  /etc/timezone
ADD monitor_logger monitor_logger
CMD ["python", "-m","monitor_logger"]