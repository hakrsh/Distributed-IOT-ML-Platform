FROM python:3.8-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN cp /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
echo "Asia/Kolkata" >  /etc/timezone
ADD platform_manager platform_manager
CMD ["python", "-m","platform_manager"]
