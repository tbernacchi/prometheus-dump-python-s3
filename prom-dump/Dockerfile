# Use the official Python base image
FROM python:3.11-alpine

# Set the working directory inside the container
WORKDIR /prometheus-dump 

# Copy the Python script into the container
COPY requirements.txt prometheus-snapshot.py /prometheus-dump/

# Install any dependencies required by the script
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt && chmod a+rwx prometheus-snapshot.py

# Set the environment variables for prometheus
ENV PROMETHEUS_URL ""

# Run the Python script when the container starts
CMD ["python3", "prometheus-snapshot.py"]
