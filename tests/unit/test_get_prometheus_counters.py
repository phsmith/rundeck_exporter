import pytest


def _by_name(metrics):
    """
    Build a mapping of metric names to metric objects.

    Returns:
    	dict: Dictionary mapping metric names to metric objects
    """
    return {m.name: m for m in metrics}


class TestGetPrometheusCounters:
    def test_rundeck_prefixed_name_kept_as_is(self, collector):
        text = (
            "# HELP rundeck_scheduler_quartz_scheduledJobs  \n"
            "# TYPE rundeck_scheduler_quartz_scheduledJobs gauge\n"
            "rundeck_scheduler_quartz_scheduledJobs 4.0\n"
        )
        families = _by_name(list(collector._get_prometheus_counters(text)))
        assert "rundeck_scheduler_quartz_scheduledJobs" in families

    def test_non_rundeck_name_gets_prefixed(self, collector):
        text = (
            "# HELP jvm_threads_live_threads Live threads\n"
            "# TYPE jvm_threads_live_threads gauge\n"
            "jvm_threads_live_threads 65.0\n"
        )
        families = _by_name(list(collector._get_prometheus_counters(text)))
        assert "rundeck_jvm_threads_live_threads" in families
        assert "jvm_threads_live_threads" not in families

    def test_execution_status_samples_excluded(self, collector):
        text = (
            "# HELP rundeck_execution_status_running  \n"
            "# TYPE rundeck_execution_status_running gauge\n"
            "rundeck_execution_status_running 1.0\n"
        )
        assert list(collector._get_prometheus_counters(text)) == []

    def test_instance_address_label_added_to_every_sample(self, collector):
        text = (
            "# HELP executor_active_threads Active threads\n"
            "# TYPE executor_active_threads gauge\n"
            'executor_active_threads{name="applicationTaskExecutor"} 0.0\n'
        )
        families = _by_name(list(collector._get_prometheus_counters(text)))
        sample = families["rundeck_executor_active_threads"].samples[0]
        assert sample.labels["instance_address"] == collector.instance_address
        assert sample.labels["name"] == "applicationTaskExecutor"

    def test_summary_type_preserves_count_and_sum_samples(self, collector):
        text = (
            "# HELP http_server_requests_seconds  \n"
            "# TYPE http_server_requests_seconds summary\n"
            'http_server_requests_seconds_count{status="200"} 105\n'
            'http_server_requests_seconds_sum{status="200"} 0.995913301\n'
        )
        families = _by_name(list(collector._get_prometheus_counters(text)))
        family = families["rundeck_http_server_requests_seconds"]
        assert family.type == "summary"
        sample_names = {s.name for s in family.samples}
        assert sample_names == {
            "rundeck_http_server_requests_seconds_count",
            "rundeck_http_server_requests_seconds_sum",
        }

    @pytest.mark.parametrize("metric_type", ["counter", "gauge"])
    def test_type_passthrough(self, collector, metric_type):
        text = (
            f"# HELP some_metric  \n"
            f"# TYPE some_metric {metric_type}\n"
            "some_metric 1.0\n"
        )
        families = _by_name(list(collector._get_prometheus_counters(text)))
        assert families["rundeck_some_metric"].type == metric_type
