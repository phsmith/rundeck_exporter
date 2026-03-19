# Rundeck Exporter Helm Chart

Helm chart to deploy [Rundeck Exporter](https://github.com/phsmith/rundeck_exporter) on Kubernetes — a Prometheus exporter that collects metrics and information from Rundeck for monitoring with Prometheus and Grafana.

## Prerequisites

- Kubernetes 1.19+
- Helm 3+
- A running Rundeck instance accessible from the cluster
- Prometheus (and optionally Grafana) for metrics collection and visualization
- [prometheus-operator](https://github.com/prometheus-operator/kube-prometheus) — required only if `serviceMonitor.enabled=true`

## Installation

```bash
# Clone the repository
git clone https://github.com/phsmith/rundeck_exporter.git
cd rundeck_exporter

# Install with default values
helm install rundeck-exporter --create-namespace --namespace monitoring ./charts

# Install with custom values file
helm install rundeck-exporter --create-namespace --namespace monitoring \
  -f ./charts/values.yaml ./charts

# Install with inline overrides
helm install rundeck-exporter --create-namespace --namespace monitoring \
  --set env.RUNDECK_URL=http://rundeck:4440 \
  --set env.RUNDECK_TOKEN=your-token \
  ./charts
```

## Authentication

The exporter supports two authentication methods:

**Token-based (recommended):**

```bash
--set env.RUNDECK_TOKEN=your-rundeck-auth-token
```

**Username/password:**

```bash
--set env.RUNDECK_USERNAME=admin \
--set env.RUNDECK_USERPASSWORD=secret
```

To avoid exposing credentials in plain text, use `envSecret` to load them from an existing Kubernetes secret:

```bash
# Create the secret
kubectl create secret generic rundeck-exporter-token \
  --namespace monitoring \
  --from-literal=RUNDECK_TOKEN=your-rundeck-auth-token

# Reference it in the chart
--set envSecret=rundeck-exporter-token
```

## Configuration

| Parameter | Description | Default |
| --------- | ----------- | ------- |
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Container image repository | `phsmith/rundeck-exporter` |
| `image.tag` | Container image tag | `3.1.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `env.RUNDECK_URL` | Rundeck base URL | `http://localhost:4440` |
| `env.RUNDECK_TOKEN` | Rundeck auth token | `""` |
| `env.RUNDECK_USERNAME` | Rundeck username (session auth) | `""` |
| `env.RUNDECK_USERPASSWORD` | Rundeck password (session auth) | `""` |
| `env.RUNDECK_API_VERSION` | Rundeck API version | `40` |
| `env.RUNDECK_SKIP_SSL` | Skip SSL verification | `false` |
| `env.RUNDECK_PROJECTS_EXECUTIONS` | Collect per-project execution metrics | `true` |
| `env.RUNDECK_PROJECTS_EXECUTIONS_CACHE` | Cache execution requests | `false` |
| `env.RUNDECK_CPU_STATS` | Collect CPU stats | `true` |
| `env.RUNDECK_MEMORY_STATS` | Collect memory stats | `true` |
| `envSecret` | Name of existing secret to load env vars from | `""` |
| `service.port` | Service port | `9620` |
| `probe.enabled` | Enable liveness/readiness probes | `true` |
| `serviceMonitor.enabled` | Create a Prometheus Operator ServiceMonitor | `true` |
| `serviceMonitor.interval` | Scrape interval | `30s` |
| `serviceMonitor.scrapeTimeout` | Scrape timeout | `10s` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |
| `resources.limits.cpu` | CPU limit | `200m` |
| `resources.limits.memory` | Memory limit | `256Mi` |
| `autoscaling.enabled` | Enable HPA | `false` |

See [values.yaml](values.yaml) for the full list of options.

## ServiceMonitor (Prometheus Operator)

When `serviceMonitor.enabled=true`, a `ServiceMonitor` resource is created so Prometheus Operator automatically scrapes the exporter. This requires the [prometheus-operator CRDs](https://github.com/prometheus-operator/prometheus-operator) to be installed in the cluster.

If you are not using Prometheus Operator, disable it:

```bash
--set serviceMonitor.enabled=false
```

## Upgrade

```bash
helm upgrade rundeck-exporter --namespace monitoring -f ./charts/values.yaml ./charts
```

## Uninstall

```bash
helm uninstall rundeck-exporter --namespace monitoring
```
