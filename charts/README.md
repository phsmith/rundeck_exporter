# Rundeck Exporter Helm Chart

This is a Helm Chart project to deploy Rundeck Exporter on Kubernetes.

## Description

Rundeck Exporter was developed by Phillipe Smith and is part of the Rundeck community contribution, it is a tool that collects metrics and information from Rundeck for monitoring and observability using Prometheus and Grafana for data display friendly. This Chart facilitates deployment and configuration of Rundeck Exporter in a Kubernetes cluster.

## Prerequisites

- A working Kubernetes cluster.
- Rundeck, Prometheus and Grafana.
- Helm 3 or higher installed.

## Installation

1.Clone the repository

```
git clone https://github.com/nataliagranato/rundeck_exporter.git
```

2.Access the charts directory

```
cd charts 
```

3.Create namespace (if no):

```
kubectl create namespace my-namespace
```

4.Install the Rundeck Exporter:

```
helm install rundeck-exporter -n your-namespace .
```

## Configuration

The Rundeck Exporter configuration can be customized by editing the values.yaml file or by using the --set option during installation.

Here are some common settings:

'image.repository': The Rundeck Exporter image repository.
'image.tag': The tag of the Rundeck Exporter image.
'replicaCount': The number of replicas desired for Rundeck Exporter.
'service.port': The port on which Rundeck Exporter exposes metrics.
'env': Environment variables to configure Rundeck Exporter.

See the values.yaml file for all available configuration options.

## Customization

You can further customize the Rundeck Exporter deployment by editing the deployment.yaml file in the templates directory. Here you can add volumes, define resources, configure readiness and vitality probes, among other options.

## Removal

To remove Rundeck Exporter, run the following command:

```
helm uninstall rundeck-exporter
```

This will remove all Rundeck Exporter related resources from the Kubernetes cluster.
