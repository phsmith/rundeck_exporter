# ServiceMonitor for Rundeck Exporter

The ServiceMonitor is a resource used by the Prometheus Operator to discover service endpoints in Kubernetes. In this case, we will create a ServiceMonitor to control the Rundeck exporter.

## Pre-element

Prometheus Operator install in the Kubernetes cluster. The Prometheus Operator is help you create monitoring resources, such as ServiceMonitor. ServiceMonitor.

## Go to ServiceMonitor

1. Create a YAML file for the ServiceMonitor. For example, service-monitor.yaml.

2. Open the service-monitor.yaml file in a text editor and hints as information:

```
apiVersion: monitoring.coreos.com/v1
type: ServiceMonitor
metadata:
  name: my-service-monitor
labels:
    app: rundeck-exporter
spec:
  selector:
    matchLabels:
    application: reporter's endpoint
:
    - port: 9620
    range: 30s
    path: /metrics
```

Get started with my service-monitor by name for ServiceMonitor. You can also get port value if Rundeck Exporter nations on a different port.

3. Save the file service - monitor.yaml with the information.

4. Use the kubectl command to sign the ServiceMonitor file:

```
kubectl apply -f service-monitor.yaml -n your-namespace-rundeck
```

## Verifying the ServiceMonitor

After setting the ServiceMonitor, you can verify that it is being displayed, prohibited, and monitored by the Prometheus Operator.

1.

``
kubectl get my-service-monitor servicemonitor

```

 tap on the fun ServiceMonitor including name, labels and other details.

2. Vulnerability if the Prometheus Operator detected the ServiceMonitor:

```

kubectl get promisedheusrules --all-namespaces
``

This shows how monitoring rules by the Prometheus Operator. You should see a post to ServiceMonitor create.

3. ← if Rundeck Exporter skills are related to Prometheus:

* Access the Prometheus UI using a Browser:

```
http://<prometheus-endpoint>
```

Replace <prometheus-endpoint> with the Prometheus service target in your Kubernetes cluster.

* to the "Status" section in the Prometheus UI and details if the Rundeck Exporter is a scrape hope reason (detail collection).

* You can also check if Prometheus is being approved for Rundeck Exporter national authorities.

## Final Considerations

With the past ServiceMonitor, the Prometheus Operator will now be considered the Rundeck Exporter and details for analysis and visualization in Prometheus.

Remember that Rundeck Exporter must be referenced, such as a port and the path to skills, for ServiceMonitor to work.

The name of the ServiceMonitor name and other details, according to your specific configuration.

ServiceMonitor for Rundeck Exporter. If you have more information about the subject. I'm here to help!
