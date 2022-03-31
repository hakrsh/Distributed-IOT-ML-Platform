FROM python:3
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD platform_manager platform_manager
CMD ["python", "-m","platform_manager"]
