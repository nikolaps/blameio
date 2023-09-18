# Use Debian Bullseye as base image
FROM debian:bullseye

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.9, pip, and collectd
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3.9 python3-pip collectd && \
    rm -rf /var/lib/apt/lists/*

COPY script.py /usr/src/app/script.py
# Set Python 3.9 as the default Python version
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

# Install required Python packages
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip3 install -r /usr/src/app/requirements.txt

# Copy the collectd configuration file
COPY collectd.conf /etc/collectd/collectd.conf

# Run collectd in foreground mode
CMD ["/usr/sbin/collectd", "-f"]
