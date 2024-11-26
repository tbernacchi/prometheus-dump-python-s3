# prometheus-dump-s3

## Description

This repo contains a script that dumps the Prometheus data compressed into a tar.gz file and uploads it to an S3.

> The main idea of this was to practice a little bit of Python.

## Features

- Dumps the Prometheus data to a tar.gz file;
- Mounts and runs a script to upload the tar.gz file to an S3.

## Requirements

- Prometheus up and running (Mine was installed by [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack);<br>
- Enable snapshot through Prometheus API. More info [here](https://prometheus.io/docs/prometheus/latest/querying/api/#tsdb-admin-apis)

```
kubectl -n monitoring patch prometheus my-kube-prometheus-stack-prometheus --type merge --patch '{"spec":{"enableAdminAPI":true}}'
```

## Usage

1. Be attention to the RBAC roles needed to be created first. See `k8s/001-rbac*`;
2. Build the Docker image on `prom-dump` directory and push it to your container registry;
3. Create the ConfigMap `k8s/003-configmap-upload-s3.yaml` for the script `upload_to_s3.py`.
4. Before setting up the cronjob, you're going to need to patch the `statefulset` of Prometheus. 

> (I'm not proud of this.)
- AWS credentials;
- S3 bucket name; 
- the script mount path.

```
kubectl patch statefulset prometheus-my-kube-prometheus-stack-prometheus -n monitoring --patch '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "prometheus",
          "env": [
            {
              "name": "AWS_ACCESS_KEY_ID",
              "valueFrom": {
                "secretKeyRef": {
                  "name": "aws-credentials",
                  "key": "aws_access_key_id"
                }
              }
            },
            {
              "name": "AWS_SECRET_ACCESS_KEY",
              "valueFrom": {
                "secretKeyRef": {
                  "name": "aws-credentials",
                  "key": "aws_secret_access_key"
                }
              }
            }
          ]
        }]
      }
    }
  }
}'
```

```
kubectl patch statefulset prometheus-my-kube-prometheus-stack-prometheus -n monitoring --patch '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "prometheus",
          "env": [{
            "name": "S3_BUCKET",
            "value": "prometheus-snapshot"
          }]
        }]
      }
    }
  }
}'
```

```
kubectl patch statefulset prometheus-my-kube-prometheus-stack-prometheus -n monitoring --patch '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "prometheus",
          "volumeMounts": [{
            "name": "upload-script",
            "mountPath": "/prometheus/upload_to_s3.py",
            "subPath": "upload_to_s3.py"
          }]
        }],
        "volumes": [{
          "name": "upload-script",
          "configMap": {
            "name": "s3-upload-script"
          }
        }]
      }
    }
  }
}'
```

5. Create the Kubernetes cronjob to run the script at a specific interval.

```
kubectl apply -f k8s/002-cronjob-prometheus-dump.yaml
```

More elegant way to accomplish this:

[Thanos Sidecar](https://thanos.io/tip/components/sidecar.md/)<br>
[Integration of Thanos with Prometheus and S3 as storage](https://medium.com/@shubhamjadhav957/integration-of-thanos-with-prometheus-and-s3-as-storage-731e8d0a773f)
