FROM python:3.8-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN cp /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
echo "Asia/Kolkata" >  /etc/timezone
ADD model_request_handler model_request_handler
CMD ["python", "-m","model_request_handler"]
