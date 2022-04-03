FROM python:3
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN ls /usr/share/zoneinfo && \
cp /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
echo "Africa/Lusaka" >  /etc/timezone
ADD scheduler scheduler
CMD ["python", "-m","scheduler"]
