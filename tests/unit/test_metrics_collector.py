from unittest.mock import patch


class TestRundeckMetricsCollector:
    def test_scrape_duration_on_request_failure(self, collector):
        """collect() must yield a non-negative scrape duration even when all requests fail."""
        with patch("rundeck_exporter.metrics_collector.request", return_value=None):
            duration_metrics = [m for m in collector.collect() if m.name == "rundeck_exporter_scrape_duration_seconds"]

        assert len(duration_metrics) == 1
        assert duration_metrics[0].samples[0].value >= 0

    def test_executor_reused_across_scrapes(self, collector):
        """self.executor must be created once at __init__ and reused on every collect()."""
        executor_id = id(collector.executor)

        with patch("rundeck_exporter.metrics_collector.request", return_value=None):
            list(collector.collect())
            list(collector.collect())

        assert id(collector.executor) == executor_id

    def test_scrape_duration_yielded_in_passive_mode_early_return(self, collector):
        """collect() must yield scrape duration when passive-mode guard aborts the scrape."""
        system_info = {
            "system": {
                "executions": {"executionMode": "passive"},
                "rundeck": {"version": "3.0", "node": "test-node"},
            }
        }
        metrics_data = {"counters": {}, "gauges": {}, "meters": {}, "timers": {}}

        def _mock_request(endpoint):
            return system_info if endpoint == "/system/info" else metrics_data

        with patch("rundeck_exporter.metrics_collector.request", side_effect=_mock_request):
            with patch.object(collector.args, "no_checks_in_passive_mode", True):
                names = [m.name for m in collector.collect()]

        assert "rundeck_exporter_scrape_duration_seconds" in names

    def test_concurrent_scrape_guard_skips_project_metrics_and_yields_duration(self, collector):
        """When _execution_scrape_lock is held, collect() must skip project execution metrics but still yield duration."""
        system_info = {
            "system": {
                "executions": {"executionMode": "active"},
                "rundeck": {"version": "3.0", "node": "test-node"},
                "stats": {},
            }
        }
        metrics_data = {"counters": {}, "gauges": {}, "meters": {}, "timers": {}}

        def _mock_request(endpoint):
            if endpoint == "/system/info":
                return system_info
            if endpoint == "/projects":
                return []
            return metrics_data

        with patch("rundeck_exporter.metrics_collector.request", side_effect=_mock_request):
            with patch.object(collector.args, "rundeck_projects_executions", True):
                collector._execution_scrape_lock.acquire()
                try:
                    names = [m.name for m in collector.collect()]
                finally:
                    collector._execution_scrape_lock.release()

        assert "rundeck_exporter_scrape_duration_seconds" in names
        assert "rundeck_project_start_timestamp" not in names
        assert "rundeck_project_executions" not in names

    def test_scrape_duration_yielded_at_end_of_full_collect(self, collector):
        """On a successful full scrape, scrape duration must be the last metric yielded."""
        system_info = {
            "system": {
                "executions": {"executionMode": "active"},
                "rundeck": {"version": "3.0", "node": "test-node"},
                "stats": {},
            }
        }
        metrics_data = {"counters": {}, "gauges": {}, "meters": {}, "timers": {}}

        def _mock_request(endpoint):
            return system_info if endpoint == "/system/info" else metrics_data

        with patch("rundeck_exporter.metrics_collector.request", side_effect=_mock_request):
            with patch.object(collector.args, "rundeck_projects_executions", False):
                all_metrics = list(collector.collect())

        assert all_metrics[-1].name == "rundeck_exporter_scrape_duration_seconds"
