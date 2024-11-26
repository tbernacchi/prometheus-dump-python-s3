# First stage: Get Python
FROM python:3.11-slim as python

# Final stage: Prometheus with Python
FROM quay.io/prometheus/prometheus:v2.55.1

USER root

# Copy all necessary Python files and libraries at once
COPY --from=python /usr/local/bin/python3* /usr/local/bin/
COPY --from=python /usr/local/lib/ /usr/local/lib/
COPY --from=python /lib/ /lib/

# Install pip
COPY --from=python /usr/local/bin/pip* /usr/local/bin/
COPY --from=python /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Add Python to PATH
ENV PATH="/usr/local/bin:${PATH}"

# Install boto3
RUN pip3 install --no-cache-dir boto3

USER nobody