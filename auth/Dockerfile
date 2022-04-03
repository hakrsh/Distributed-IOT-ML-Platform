FROM python:3
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD auth auth
CMD ["python", "-m","auth"]
