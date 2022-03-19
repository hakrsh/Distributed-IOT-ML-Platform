FROM python:3
ADD model model
WORKDIR /model
RUN pip install -r requirements.txt
CMD [ "python3","server.py" ]