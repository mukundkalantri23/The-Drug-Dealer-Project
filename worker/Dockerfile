FROM xserrat/facebook-demucs:latest
WORKDIR /
RUN pip3 install --upgrade minio redis requests
COPY worker-server.py /
ENTRYPOINT python3 worker-server.py