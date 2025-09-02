import pytest
from prometheus_client.core import REGISTRY
from rundeck_exporter.metrics_collector import RundeckMetricsCollector


@pytest.fixture(scope="module")
def metrics():
    rundeck_metrics = RundeckMetricsCollector()
    REGISTRY.register(rundeck_metrics)
    return REGISTRY


@pytest.fixture()
def metric_samples(request, metrics):
    samples = []

    for metric in metrics.collect():
        for sample in metric.samples:
            if sample.name.startswith(request.param):
                samples.append(sample)

    assert len(sample) > 0
    return samples


@pytest.mark.parametrize("metric_samples", ["rundeck_system_info"], indirect=True)
def test_metric_rundeck_system_info(metric_samples):
    assert metric_samples[0].value == 1
    for label in metric_samples[0].labels.keys():
        assert label in [
            "apiversion",
            "base",
            "build",
            "buildGit",
            "instance_address",
            "node",
            "serverUUID",
            "version",
        ]


@pytest.mark.parametrize("metric_samples", ["rundeck_services"], indirect=True)
def test_metric_rundeck_services(metric_samples):
    for metric in metric_samples:
        for label in metric.labels.keys():
            assert label in [
                "instance_address",
                "rundeck_services_AuthorizationService_getSystemAuthorization_total",
                "rundeck_services_AuthorizationService_sourceCache_evictionCount",
                "rundeck_services_AuthorizationService_sourceCache_hitCount",
                "rundeck_services_AuthorizationService_sourceCache_loadExceptionCount",
                "rundeck_services_AuthorizationService_sourceCache_missCount",
                "rundeck_services_AuthorizationService_systemAuthorization_evaluateMeter_total",
                "rundeck_services_AuthorizationService_systemAuthorization_evaluateSetMeter_total",
                "rundeck_services_AuthorizationService_systemAuthorization_evaluateSetTimer_total",
                "rundeck_services_AuthorizationService_systemAuthorization_evaluateTimer_total",
                "rundeck_services_ExecutionService_executionFailureMeter_total",
                "rundeck_services_ExecutionService_executionJobStartMeter_total",
                "rundeck_services_ExecutionService_executionStartMeter_total",
                "rundeck_services_ExecutionService_executionSuccessMeter_total",
                "rundeck_services_FrameworkService_filterNodeSet_total",
                "rundeck_services_NodeService_nodeCache_evictionCount",
                "rundeck_services_NodeService_nodeCache_hitCount",
                "rundeck_services_NodeService_nodeCache_loadExceptionCount",
                "rundeck_services_NodeService_nodeCache_missCount",
                "rundeck_services_NodeService_project_test1_loadNodes_total",
                "rundeck_services_ProjectManagerService_fileCache_evictionCount",
                "rundeck_services_ProjectManagerService_fileCache_hitCount",
                "rundeck_services_ProjectManagerService_fileCache_loadExceptionCount",
                "rundeck_services_ProjectManagerService_fileCache_missCount",
                "rundeck_services_ProjectManagerService_projectCache_evictionCount",
                "rundeck_services_ProjectManagerService_projectCache_hitCount",
                "rundeck_services_ProjectManagerService_projectCache_loadExceptionCount",
                "rundeck_services_ProjectManagerService_projectCache_missCount",
            ]


@pytest.mark.parametrize("metric_samples", ["rundeck_execution_mode"], indirect=True)
def test_metric_rundeck_execution_mode(metric_samples):
    for metric in metric_samples:
        assert metric.value in (0, 1)

        for label in metric.labels.keys():
            assert label in ["instance_address"]


@pytest.mark.parametrize("metric_samples", ["rundeck_system_stats"], indirect=True)
def test_metric_rundeck_system_stats(metric_samples):
    for metric in metric_samples:
        for label in metric.labels.keys():
            assert label in [
                "instance_address",
                "rundeck_system_stats_cpu_loadAverage_ratio",
                "rundeck_system_stats_memory_free_bytes",
                "rundeck_system_stats_memory_max_bytes",
                "rundeck_system_stats_memory_total_bytes",
                "rundeck_system_stats_scheduler_running",
                "rundeck_system_stats_scheduler_threadPoolSize",
                "rundeck_system_stats_threads_active",
                "rundeck_system_stats_uptime_since",
            ]


@pytest.mark.parametrize(
    "metric_samples", ["rundeck_project_start_timestamp", "rundeck_project_execution_duration_seconds"], indirect=True
)
def test_metric_rundeck_project_times(metric_samples):
    assert isinstance(metric_samples[0].timestamp, float)
    assert isinstance(metric_samples[0].value, int) or isinstance(metric_samples[0].value, float)

    for label in metric_samples[0].labels.keys():
        assert label in [
            "execution_id",
            "execution_type",
            "instance_address",
            "job_group",
            "job_id",
            "job_name",
            "project_name",
            "user",
        ]


@pytest.mark.parametrize("metric_samples", ["rundeck_project_execution_status"], indirect=True)
def test_metric_rundeck_project_execution_status(metric_samples):
    for metric in metric_samples:
        assert metric.value in (0, 1)
        assert metric.labels.get("status") in [
            "aborted",
            "failed",
            "running",
            "succeeded",
            "unknown",
        ]

        for label in metric.labels.keys():
            assert label in [
                "execution_id",
                "execution_type",
                "instance_address",
                "job_group",
                "job_id",
                "job_name",
                "project_name",
                "status",
                "user",
            ]


@pytest.mark.parametrize(
    "metric_samples", ["rundeck_project_executions_total", "rundeck_project_nodes_total"], indirect=True
)
def test_metric_rundeck_project_totals(metric_samples):
    for metric in metric_samples:
        assert metric.value > 0

        for label in metric.labels.keys():
            assert label in ["instance_address", "project_name"]
