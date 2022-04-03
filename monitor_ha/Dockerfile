FROM python:3
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN ls /usr/share/zoneinfo && \
cp /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
ADD monitor_ha monitor_ha
CMD ["python","-m","monitor_ha"]