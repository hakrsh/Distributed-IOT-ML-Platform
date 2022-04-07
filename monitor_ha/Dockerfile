FROM python:3.8-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN cp /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
echo "Asia/Kolkata" >  /etc/timezone
ADD monitor_ha monitor_ha
CMD ["python","-m","monitor_ha"]