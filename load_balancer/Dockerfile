FROM python:3.8-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD load_balancer load_balancer
CMD ["python","-m","load_balancer"]