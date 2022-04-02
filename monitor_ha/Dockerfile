FROM python:3
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD monitor_ha monitor_ha
CMD ["python","-m","monitor_ha"]