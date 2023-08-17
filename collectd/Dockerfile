FROM collectd/collectd

# Install Python and required libraries
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Copy the Python script into the container
COPY script.py /usr/src/app/script.py

# Install Python dependencies
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip3 install --no-cache-dir -r /usr/src/app/requirements.txt

# Copy the collectd.conf configuration file
COPY collectd.conf /etc/collectd/collectd.conf

CMD ["collectd", "-f"]
