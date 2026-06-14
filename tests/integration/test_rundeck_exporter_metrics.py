import pytest
from prometheus_client.core import REGISTRY

from rundeck_exporter.metrics_collector import RundeckMetricsCollector

_EXECUTION_LABELS = {
    "execution_id",
    "execution_type",
    "instance_address",
    "job_group",
    "job_id",
    "job_name",
    "job_options",
    "project_name",
    "user",
}


@pytest.fixture(scope="module")
def metrics():
    """
    Provide the Prometheus REGISTRY with Rundeck metrics for module tests.
    
    Yields:
        REGISTRY: The global Prometheus registry with RundeckMetricsCollector registered.
    """
    rundeck_metrics = RundeckMetricsCollector()
    REGISTRY.register(rundeck_metrics)
    yield REGISTRY
    REGISTRY.unregister(rundeck_metrics)


@pytest.fixture()
def metric_samples(request, metrics):
    """
    Collect Prometheus metric samples whose names start with the requested prefix.
    
    Filters samples from the metrics fixture by the parameterized metric name prefix.
    Fails if no matching samples are found.
    
    Parameters:
        request: Pytest fixture parameter containing the metric name prefix to match
        metrics: Prometheus metrics fixture providing collected metrics
    
    Returns:
        list: Prometheus metric samples matching the requested prefix
    """
    samples = []

    for metric in metrics.collect():
        for sample in metric.samples:
            if sample.name.startswith(request.param):
                samples.append(sample)

    assert samples, f"No '{request.param}' metrics collected — is Rundeck running on localhost:4440?"
    return samples


@pytest.mark.parametrize("metric_samples", ["rundeck_system_info"], indirect=True)
def test_metric_rundeck_system_info(metric_samples):
    assert metric_samples[0].value == 1
    assert set(metric_samples[0].labels.keys()) <= {
        "apiversion",
        "base",
        "build",
        "buildGit",
        "instance_address",
        "node",
        "serverUUID",
        "version",
    }


@pytest.mark.parametrize("metric_samples", ["rundeck_services"], indirect=True)
def test_metric_rundeck_services(metric_samples):
    for metric in metric_samples:
        assert set(metric.labels.keys()) <= {"instance_address"}


@pytest.mark.parametrize("metric_samples", ["rundeck_execution_mode"], indirect=True)
def test_metric_rundeck_execution_mode(metric_samples):
    for metric in metric_samples:
        assert metric.value in (0, 1)
        assert set(metric.labels.keys()) <= {"instance_address"}


@pytest.mark.parametrize("metric_samples", ["rundeck_system_stats_threads_active"], indirect=True)
def test_metric_rundeck_system_stats(metric_samples):
    for metric in metric_samples:
        assert set(metric.labels.keys()) <= {"instance_address"}


@pytest.mark.parametrize(
    "metric_samples", ["rundeck_project_start_timestamp", "rundeck_project_execution_duration_seconds"], indirect=True
)
def test_metric_rundeck_project_times(metric_samples):
    assert isinstance(metric_samples[0].timestamp, float)
    assert isinstance(metric_samples[0].value, (int, float))
    assert set(metric_samples[0].labels.keys()) <= _EXECUTION_LABELS


@pytest.mark.parametrize("metric_samples", ["rundeck_project_execution_status"], indirect=True)
def test_metric_rundeck_project_execution_status(metric_samples):
    for metric in metric_samples:
        assert metric.value in (0, 1)
        assert metric.labels.get("status") in {"aborted", "failed", "running", "succeeded", "unknown"}
        assert set(metric.labels.keys()) <= _EXECUTION_LABELS | {"status"}


@pytest.mark.parametrize(
    "metric_samples", ["rundeck_project_executions", "rundeck_project_nodes_total"], indirect=True
)
def test_metric_rundeck_project_totals(metric_samples):
    for metric in metric_samples:
        assert metric.value > 0
        assert set(metric.labels.keys()) <= {"instance_address", "project_name"}
