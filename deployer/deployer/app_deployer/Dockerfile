FROM python:3
ADD app app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python3", "src/app.py","model_contract.json"]