FROM python:3
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD system_monitor system_monitor
CMD ["python","-m","system_monitor"]