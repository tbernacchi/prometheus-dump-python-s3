# Use the official Python base image
FROM python:3.11-alpine

# Set the working directory inside the container
WORKDIR /prometheus-purge 

# Copy the Python script into the container
COPY requirements.txt prometheus-purge.py /prometheus-purge/

# Install any dependencies required by the script
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt && chmod a+rwx prometheus-purge.py

# Set the environment variables for prometheus
ENV PROMETHEUS_URL ""

# Run the Python script when the container starts
CMD ["python3", "prometheus-purge.py"]
