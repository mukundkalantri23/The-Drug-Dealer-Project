FROM python:3.8

LABEL MAINTAINER="mukundkalantri23@gmail.com"

RUN pip3 install --upgrade flask requests minio redis jsonpickle flask-mysql cryptography pandas

WORKDIR /srv

COPY  rest-server.py /srv

COPY  data/medicine_details.csv /srv

ENV FLASK_APP=rest-server.py

CMD [ "python3", "./rest-server.py"]
