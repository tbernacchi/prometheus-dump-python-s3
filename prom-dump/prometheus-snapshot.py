#!/usr/local/bin/python3
import requests
import urllib3
import sys
from kubernetes import client, config
from kubernetes.stream import stream
import os
import tarfile
import boto3

# Load the Kubernetes configuration
try:
    config.load_incluster_config()
except:
    config.load_kube_config()

# Initialize the Kubernetes client
v1 = client.CoreV1Api()
namespace = "monitoring"

# Find the Prometheus service
services = v1.list_namespaced_service(namespace=namespace)
prometheus_service = None
for svc in services.items:
    ports = [port.port for port in svc.spec.ports]
    if 9090 in ports and 8080 in ports:
        prometheus_service = svc
        break

if not prometheus_service:
    print("Prometheus service not found.")
    sys.exit(0)

# I have a ingress rule on /prometheus.
prometheus_ip = prometheus_service.spec.cluster_ip
prometheus_url = f"http://{prometheus_ip}:9090/prometheus/api/v1/admin/tsdb/snapshot"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Request to create the snapshot
response = requests.post(prometheus_url, verify=False)
if response.status_code != 200:
    print("Error creating snapshot:", response.status_code, response.text)
    sys.exit(0)

snapshot_name = response.json()['data']['name']
print(f"Snapshot created: {snapshot_name}")

# Find the Prometheus pod
pods = v1.list_namespaced_pod(namespace=namespace)
prometheus_pod = None
for pod in pods.items:
    if pod.metadata.name.endswith("prometheus-0"):
        prometheus_pod = pod.metadata.name
        prometheus_container = pod.spec.containers[0].name
        break

if not prometheus_pod:
    print("No pod ending with 'prometheus-0' found.")
    sys.exit(1)

print(f"Prometheus pod: {prometheus_pod}")
print(f"Prometheus container: {prometheus_container}")
#prometheus_pod = pods.items[0].metadata.name

snapshot_path = "/prometheus/snapshots/"

# List directories in the pod
exec_command = ["ls", "-t", snapshot_path]
response = stream(
    v1.connect_get_namespaced_pod_exec, 
    prometheus_pod, 
    namespace, 
    container=prometheus_container, 
    command=exec_command, 
    stderr=True, 
    stdin=False, 
    stdout=True, 
    tty=False
)
newest_directory = response.splitlines()[0]
print(f"The newest directory is: {newest_directory}")

# Command to create the tar.gz - Modified to only tar the specific snapshot we just created
output_filename = f"{snapshot_path}{snapshot_name}.tar.gz"
exec_command = ["tar", "-czf", output_filename, "-C", snapshot_path, snapshot_name]

# Execute the command in the pod
response = stream(
    v1.connect_get_namespaced_pod_exec, 
    prometheus_pod, 
    namespace, 
    container=prometheus_container, 
    command=exec_command, 
    stderr=True, 
    stdin=False, 
    stdout=True, 
    tty=False
)

exec_command = [
    "python3",
    "/prometheus/upload_to_s3.py",
]

print(f"Upload command: {exec_command}")

# Execute the command in the pod and check the response
response = stream(
    v1.connect_get_namespaced_pod_exec,
    prometheus_pod,
    namespace,
    container=prometheus_container,
    command=exec_command,
    stderr=True,
    stdin=False,
    stdout=True,
    tty=False
)

print(f"Upload response: {response}")

# Cleanup the local tar file after upload
cleanup_command = ["rm", "-f", output_filename]
stream(
    v1.connect_get_namespaced_pod_exec,
    prometheus_pod,
    namespace,
    container=prometheus_container,
    command=cleanup_command,
    stderr=True,
    stdin=False,
    stdout=True,
    tty=False
)

# Exit after everything is done
sys.exit(0)