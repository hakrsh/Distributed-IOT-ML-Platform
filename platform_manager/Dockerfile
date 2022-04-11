FROM python:3.8-slim
COPY requirements.txt .
RUN apt-get update && apt-get install -y vim curl sshpass && curl -sL https://aka.ms/InstallAzureCLIDeb | bash
RUN pip install -r requirements.txt
RUN cp /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
echo "Asia/Kolkata" >  /etc/timezone
ADD platform_manager platform_manager
CMD ["python", "-m","platform_manager"]
