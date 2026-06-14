from unittest.mock import patch

import pytest

from rundeck_exporter.constants import RUNDECK_EXECUTION_STATUSES
from rundeck_exporter.metrics_collector import RundeckProjectExecution


def _make_execution(exec_id: int, status: str = "succeeded", has_start: bool = True) -> dict:
    """
    Build a Rundeck execution dict for testing.
    
    Parameters:
        exec_id (int): The execution ID.
        status (str): The execution status. Defaults to "succeeded".
        has_start (bool): Whether to include start and end timestamps. Defaults to True.
    
    Returns:
        dict: A mock Rundeck execution dict.
    """
    base = {
        "id": exec_id,
        "status": status,
        "executionType": "scheduled",
        "user": "admin",
        "job": {"id": f"job-{exec_id}", "name": "test-job", "group": ""},
    }
    if has_start:
        base["date-started"] = {"unixtime": 1_700_000_000_000}
        base["date-ended"] = {"unixtime": 1_700_000_010_000}
    return base


def _mock_responses(running: list, recent: list, total: int):
    """
    Create a mock HTTP response router for Rundeck API endpoints.
    
    Parameters:
        running (list): List of execution dicts for the running executions endpoint.
        recent (list): List of execution dicts for the recent executions endpoint.
        total (int): Total execution count for the metrics endpoint.
    
    Returns:
        function: A callable that accepts an endpoint string and returns the appropriate
                  response dict (running, recent, or metrics payload based on endpoint).
    """
    running_resp = {"executions": running}
    recent_resp = {"executions": recent}
    metrics_resp = {"total": total}

    def side_effect(endpoint):
        """
        Select and return the appropriate mock response payload based on the endpoint string.
        
        Checks the endpoint parameter to determine which response to return:
        - If "running" is in the endpoint, returns the running executions response.
        - If "metrics" is in the endpoint, returns the metrics response.
        - Otherwise, returns the recent executions response.
        
        Parameters:
        	endpoint (str): The HTTP endpoint path or URL being mocked.
        
        Returns:
        	dict: A response payload dictionary containing the appropriate mock data (running, metrics, or recent executions).
        """
        if "running" in endpoint:
            return running_resp
        if "metrics" in endpoint:
            return metrics_resp
        return recent_resp

    return side_effect


class TestGetProjectExecutions:
    def test_deduplicates_execution_ids_across_running_and_recent(self, run_project_executions):
        """An execution present in both running and recent lists must produce one record set."""
        exec1 = _make_execution(1, "running")
        records, _ = run_project_executions(_mock_responses(running=[exec1], recent=[exec1], total=0))

        start_records = [r for r in records if r.execution_type == RundeckProjectExecution.START]
        assert len(start_records) == 1

    def test_status_one_hot_per_execution(self, run_project_executions):
        """Exactly one STATUS record per execution should have value 1 (the matching status)."""
        exec1 = _make_execution(1, "succeeded")
        records, _ = run_project_executions(_mock_responses(running=[], recent=[exec1], total=1))

        status_records = [r for r in records if r.execution_type == RundeckProjectExecution.STATUS]
        assert len(status_records) == len(RUNDECK_EXECUTION_STATUSES)
        ones = [r for r in status_records if r.value == 1]
        assert len(ones) == 1
        assert ones[0].labels_value[-1] == "succeeded"

    def test_job_execution_duration_in_seconds(self, run_project_executions):
        """duration = (end_ms - start_ms) / 1000 — must be in seconds."""
        exec1 = _make_execution(1, "succeeded")
        # start=1_700_000_000_000ms, end=1_700_000_010_000ms → 10s
        records, _ = run_project_executions(_mock_responses(running=[], recent=[exec1], total=1))

        duration_records = [r for r in records if r.execution_type == RundeckProjectExecution.DURATION]
        assert len(duration_records) == 1
        assert duration_records[0].value == pytest.approx(10.0)

    def test_job_start_time_in_milliseconds(self, run_project_executions):
        """job_start_time is kept in milliseconds (historical behavior)."""
        exec1 = _make_execution(1, "succeeded")
        records, _ = run_project_executions(_mock_responses(running=[], recent=[exec1], total=1))

        start_records = [r for r in records if r.execution_type == RundeckProjectExecution.START]
        assert len(start_records) == 1
        assert start_records[0].value == 1_700_000_000_000

    def test_missing_date_started_skips_start_and_duration_but_emits_status(self, run_project_executions):
        """Without date-started: START and DURATION records must be omitted, but STATUS must still be emitted."""
        exec_no_start = _make_execution(1, "running", has_start=False)
        exec_with_start = _make_execution(2, "succeeded", has_start=True)
        records, _ = run_project_executions(_mock_responses(running=[exec_no_start], recent=[exec_with_start], total=1))

        start_records = [r for r in records if r.execution_type == RundeckProjectExecution.START]
        duration_records = [r for r in records if r.execution_type == RundeckProjectExecution.DURATION]
        status_records = [r for r in records if r.execution_type == RundeckProjectExecution.STATUS]

        # exec 1 (no start) contributes STATUS but no START/DURATION
        # exec 2 (has start) contributes all three
        assert len(start_records) == 1
        assert len(duration_records) == 1
        assert len(status_records) == 2 * len(RUNDECK_EXECUTION_STATUSES)

    @pytest.mark.parametrize("enabled,expected_label", [
        pytest.param(False, "", id="disabled-empty"),
        pytest.param(True, "env,region", id="enabled-keys-only"),
    ])
    def test_job_options_label(self, collector, run_project_executions, enabled, expected_label):
        """job_options label is empty when disabled, or comma-joined option KEYS (no values) when enabled."""
        exec1 = _make_execution(1, "succeeded")
        exec1["job"]["options"] = {"env": "prod", "region": "us"}

        with patch.object(collector.args, "rundeck_projects_executions_include_job_options", enabled):
            records, _ = run_project_executions(_mock_responses(running=[], recent=[exec1], total=1))

        start = next(r for r in records if r.execution_type == RundeckProjectExecution.START)
        # job_options is the 6th project-execution label (index 5)
        assert start.labels_value[5] == expected_label
        if enabled:
            assert "prod" not in start.labels_value[5]
            assert "us" not in start.labels_value[5]

    def test_total_executions_is_metrics_total_plus_running_count(self, run_project_executions):
        """/executions/metrics total counts completed only; running is added separately."""
        exec1 = _make_execution(1, "running")
        exec2 = _make_execution(2, "succeeded")
        _, totals = run_project_executions(_mock_responses(running=[exec1], recent=[exec2], total=5))

        assert totals["total_executions"] == 6  # 5 completed (metrics) + 1 running
