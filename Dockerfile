# Dockerfile
FROM telegraf:latest

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install mysql-connector-python && \
    rm -rf /var/lib/apt/lists/*

