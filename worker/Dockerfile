FROM python:3.8

LABEL MAINTAINER="mukundkalantri23@gmail.com"

RUN pip3 install --upgrade flask requests minio redis jsonpickle flask-mysql cryptography pandas mysql-connector-python google-cloud-vision

WORKDIR /

COPY worker-server.py /
COPY credentials.json /

CMD [ "python3", "./worker-server.py"]
