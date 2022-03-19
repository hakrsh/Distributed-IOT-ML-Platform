FROM python:3
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD deployer deployer
CMD ["python", "-m","deployer"]
