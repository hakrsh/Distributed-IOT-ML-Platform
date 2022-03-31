FROM python:3
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD deployer_master deployer_master
CMD ["python","-m","deployer_master"]
