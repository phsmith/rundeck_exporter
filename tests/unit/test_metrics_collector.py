from unittest.mock import patch

_METRICS_DATA = {"counters": {}, "gauges": {}, "meters": {}, "timers": {}}

_ACTIVE_SYSTEM_INFO = {
    "system": {
        "executions": {"executionMode": "active"},
        "rundeck": {"version": "3.0", "node": "test-node"},
        "stats": {},
    }
}

_PASSIVE_SYSTEM_INFO = {
    "system": {
        "executions": {"executionMode": "passive"},
        "rundeck": {"version": "3.0", "node": "test-node"},
    }
}

_ACTIVE_SYSTEM_INFO_V6 = {
    "system": {
        "executions": {"executionMode": "active"},
        "rundeck": {"version": "6.0.1", "node": "test-node"},
        "stats": {},
    }
}

_PROMETHEUS_METRICS_TEXT = (
    "# HELP jvm_threads_live_threads Live threads\n"
    "# TYPE jvm_threads_live_threads gauge\n"
    "jvm_threads_live_threads 42.0\n"
)


def _v6_router(endpoint, **_kwargs):
    """
    Mock HTTP endpoint responses for a Rundeck 6+ system, where metrics are served in
    Prometheus exposition format at /monitoring/prometheus instead of /metrics/metrics.
    """
    if endpoint == "/system/info":
        return _ACTIVE_SYSTEM_INFO_V6
    if endpoint == "/projects":
        return [{"name": "test1"}]
    if endpoint == "/monitoring/prometheus":
        return _PROMETHEUS_METRICS_TEXT
    return _METRICS_DATA


def _active_router(endpoint):
    """
    Mock HTTP endpoint responses for active-mode Rundeck system testing.
    
    Parameters:
    	endpoint (str): The endpoint path to mock.
    
    Returns:
    	dict or list: System information dict for "/system/info", project list for "/projects", or metrics data dict for any other endpoint.
    """
    if endpoint == "/system/info":
        return _ACTIVE_SYSTEM_INFO
    if endpoint == "/projects":
        return [{"name": "test1"}]
    return _METRICS_DATA


def _passive_router(endpoint):
    """
    Route requests to passive system info or metrics data based on the endpoint.
    
    Returns:
        dict: Passive system info dict if endpoint is "/system/info", otherwise a metrics data dict.
    """
    return _PASSIVE_SYSTEM_INFO if endpoint == "/system/info" else _METRICS_DATA


class TestRundeckMetricsCollector:
    def test_scrape_duration_on_request_failure(self, collector, mock_collect):
        """collect() must yield a non-negative scrape duration even when all requests fail."""
        with mock_collect(lambda _: None):
            duration_metrics = [m for m in collector.collect() if m.name == "rundeck_exporter_scrape_duration_seconds"]

        assert len(duration_metrics) == 1
        assert duration_metrics[0].samples[0].value >= 0

    def test_executor_reused_across_scrapes(self, collector, mock_collect):
        """self.executor must be created once at __init__ and reused on every collect()."""
        executor_id = id(collector.executor)

        with mock_collect(lambda _: None):
            list(collector.collect())
            list(collector.collect())

        assert id(collector.executor) == executor_id

    def test_scrape_duration_yielded_in_passive_mode_early_return(self, collector, mock_collect):
        """collect() must yield scrape duration when passive-mode guard aborts the scrape."""
        with mock_collect(_passive_router, no_checks_in_passive_mode=True):
            names = [m.name for m in collector.collect()]

        assert "rundeck_exporter_scrape_duration_seconds" in names

    def test_concurrent_scrape_guard_skips_project_metrics_and_yields_duration(self, collector, mock_collect):
        """When _execution_scrape_lock is held, collect() must skip execution fetching but still emit empty families and duration."""
        with mock_collect(_active_router, rundeck_projects_executions=True):
            collector._execution_scrape_lock.acquire()
            try:
                names = [m.name for m in collector.collect()]
            finally:
                collector._execution_scrape_lock.release()

        assert "rundeck_exporter_scrape_duration_seconds" in names
        # Empty families are emitted even when the lock is held (per AGENTS.md design)
        assert "rundeck_project_start_timestamp" in names
        assert "rundeck_project_executions" in names

    def test_scrape_duration_yielded_at_end_of_full_collect(self, collector, mock_collect):
        """On a successful full scrape, scrape duration must be the last metric yielded."""
        with mock_collect(_active_router, rundeck_projects_executions=False):
            all_metrics = list(collector.collect())

        assert all_metrics[-1].name == "rundeck_exporter_scrape_duration_seconds"

    def test_v6_system_fetches_native_prometheus_endpoint(self, collector, mock_collect):
        """collect() must branch to /monitoring/prometheus and _get_prometheus_counters when
        system.rundeck.version reports a major version >= 6, instead of the legacy /metrics/metrics."""
        with mock_collect(_v6_router, rundeck_projects_executions=False):
            names = [m.name for m in collector.collect()]

        assert "rundeck_jvm_threads_live_threads" in names

    def test_metrics_endpoint_bypasses_cache(self, collector):
        """The metrics endpoint (legacy or native) must always use request(), never cached_request(),
        so Prometheus counters/gauges reflect the current scrape instead of a stale cached snapshot."""
        with patch("rundeck_exporter.metrics_collector.cached_request", return_value=_ACTIVE_SYSTEM_INFO) as mock_cached:
            with patch("rundeck_exporter.metrics_collector.request", return_value=_METRICS_DATA) as mock_request:
                with patch.object(collector.args, "rundeck_projects_executions", False):
                    with patch.object(collector.args, "rundeck_projects_nodes_info", False):
                        list(collector.collect())

        mock_cached.assert_called_once_with("/system/info")
        mock_request.assert_any_call("/metrics/metrics")
