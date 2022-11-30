FROM python:3.8

LABEL MAINTAINER="mukundkalantri23@gmail.com"

RUN pip3 install --upgrade flask requests minio redis jsonpickle

WORKDIR /srv

COPY  rest-server.py /srv

ENV FLASK_APP=rest-server.py

CMD [ "python3", "./rest-server.py"]
