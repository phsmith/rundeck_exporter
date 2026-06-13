from unittest.mock import patch

import pytest

from rundeck_exporter.constants import RUNDECK_EXECUTION_STATUSES
from rundeck_exporter.metrics_collector import RundeckProjectExecution


def _make_execution(exec_id: int, status: str = "succeeded", has_start: bool = True) -> dict:
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
    running_resp = {"executions": running}
    recent_resp = {"executions": recent}
    metrics_resp = {"total": total}

    def side_effect(endpoint):
        if "running" in endpoint:
            return running_resp
        if "metrics" in endpoint:
            return metrics_resp
        return recent_resp

    return side_effect


class TestGetProjectExecutions:
    def test_deduplicates_execution_ids_across_running_and_recent(self, collector):
        """An execution present in both running and recent lists must produce one record set."""
        exec1 = _make_execution(1, "running")
        side_effect = _mock_responses(running=[exec1], recent=[exec1], total=0)

        with patch("rundeck_exporter.metrics_collector.request", side_effect=side_effect):
            records, _ = collector._get_project_executions({"name": "test1"})

        start_records = [r for r in records if r.execution_type == RundeckProjectExecution.START]
        assert len(start_records) == 1

    def test_status_one_hot_per_execution(self, collector):
        """Exactly one STATUS record per execution should have value 1 (the matching status)."""
        exec1 = _make_execution(1, "succeeded")
        side_effect = _mock_responses(running=[], recent=[exec1], total=1)

        with patch("rundeck_exporter.metrics_collector.request", side_effect=side_effect):
            records, _ = collector._get_project_executions({"name": "test1"})

        status_records = [r for r in records if r.execution_type == RundeckProjectExecution.STATUS]
        assert len(status_records) == len(RUNDECK_EXECUTION_STATUSES)
        ones = [r for r in status_records if r.value == 1]
        assert len(ones) == 1
        # The label list has status appended last; confirm it's the matching status
        assert ones[0].labels_value[-1] == "succeeded"

    def test_job_execution_duration_in_seconds(self, collector):
        """duration = (end_ms - start_ms) / 1000 — must be in seconds."""
        exec1 = _make_execution(1, "succeeded")
        # start=1_700_000_000_000ms, end=1_700_000_010_000ms → 10s
        side_effect = _mock_responses(running=[], recent=[exec1], total=1)

        with patch("rundeck_exporter.metrics_collector.request", side_effect=side_effect):
            records, _ = collector._get_project_executions({"name": "test1"})

        duration_records = [r for r in records if r.execution_type == RundeckProjectExecution.DURATION]
        assert len(duration_records) == 1
        assert duration_records[0].value == pytest.approx(10.0)

    def test_job_start_time_in_milliseconds(self, collector):
        """job_start_time is kept in milliseconds (historical behavior)."""
        exec1 = _make_execution(1, "succeeded")
        side_effect = _mock_responses(running=[], recent=[exec1], total=1)

        with patch("rundeck_exporter.metrics_collector.request", side_effect=side_effect):
            records, _ = collector._get_project_executions({"name": "test1"})

        start_records = [r for r in records if r.execution_type == RundeckProjectExecution.START]
        assert len(start_records) == 1
        assert start_records[0].value == 1_700_000_000_000

    def test_missing_date_started_skips_start_and_duration_but_emits_status(self, collector):
        """Without date-started: START and DURATION records must be omitted, but STATUS must still be emitted."""
        exec_no_start = _make_execution(1, "running", has_start=False)
        exec_with_start = _make_execution(2, "succeeded", has_start=True)
        side_effect = _mock_responses(running=[exec_no_start], recent=[exec_with_start], total=1)

        with patch("rundeck_exporter.metrics_collector.request", side_effect=side_effect):
            records, _ = collector._get_project_executions({"name": "test1"})

        start_records = [r for r in records if r.execution_type == RundeckProjectExecution.START]
        duration_records = [r for r in records if r.execution_type == RundeckProjectExecution.DURATION]
        status_records = [r for r in records if r.execution_type == RundeckProjectExecution.STATUS]

        # exec 1 (no start) contributes STATUS but no START/DURATION
        # exec 2 (has start) contributes all three
        assert len(start_records) == 1
        assert len(duration_records) == 1
        assert len(status_records) == 2 * len(RUNDECK_EXECUTION_STATUSES)

    def test_job_options_label_empty_when_disabled(self, collector):
        """With the flag off (default), job_options label is an empty string — option keys are not emitted."""
        exec1 = _make_execution(1, "succeeded")
        exec1["job"]["options"] = {"env": "prod", "region": "us"}
        side_effect = _mock_responses(running=[], recent=[exec1], total=1)

        collector.args.rundeck_projects_executions_include_job_options = False
        with patch("rundeck_exporter.metrics_collector.request", side_effect=side_effect):
            records, _ = collector._get_project_executions({"name": "test1"})

        # job_options is the 6th project-execution label (index 5 after the 1 default label)
        start = next(r for r in records if r.execution_type == RundeckProjectExecution.START)
        assert start.labels_value[5] == ""

    def test_job_options_label_emits_keys_only_when_enabled(self, collector):
        """With the flag on, job_options label holds option KEYS only (not values), comma-joined."""
        exec1 = _make_execution(1, "succeeded")
        exec1["job"]["options"] = {"env": "prod", "region": "us"}
        side_effect = _mock_responses(running=[], recent=[exec1], total=1)

        collector.args.rundeck_projects_executions_include_job_options = True
        with patch("rundeck_exporter.metrics_collector.request", side_effect=side_effect):
            records, _ = collector._get_project_executions({"name": "test1"})

        start = next(r for r in records if r.execution_type == RundeckProjectExecution.START)
        assert start.labels_value[5] == "env,region"
        # values must never leak into the label
        assert "prod" not in start.labels_value[5]
        assert "us" not in start.labels_value[5]

    def test_total_executions_is_metrics_total_plus_running_count(self, collector):
        """/executions/metrics total counts completed only; running is added separately."""
        exec1 = _make_execution(1, "running")
        exec2 = _make_execution(2, "succeeded")
        side_effect = _mock_responses(running=[exec1], recent=[exec2], total=5)

        with patch("rundeck_exporter.metrics_collector.request", side_effect=side_effect):
            _, totals = collector._get_project_executions({"name": "test1"})

        assert totals["total_executions"] == 6  # 5 completed (metrics) + 1 running
