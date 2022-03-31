FROM python:3
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD scheduler scheduler
CMD ["python", "-m","scheduler"]
