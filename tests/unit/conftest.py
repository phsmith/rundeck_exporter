from contextlib import ExitStack, contextmanager
from unittest.mock import patch

import pytest
from prometheus_client import REGISTRY

from rundeck_exporter.metrics_collector import RundeckMetricsCollector


@pytest.fixture(scope="module")
def collector():
    c = RundeckMetricsCollector()
    REGISTRY.register(c)
    try:
        yield c
    finally:
        REGISTRY.unregister(c)
        c.executor.shutdown(wait=True)


@pytest.fixture
def run_project_executions(collector):
    """Factory that patches request/cached_request and disables the executions cache, then calls _get_project_executions."""
    def _run(side_effect, project=None):
        project = project or {"name": "test1"}
        with patch("rundeck_exporter.metrics_collector.request", side_effect=side_effect):
            with patch.object(collector.args, "rundeck_projects_executions_cache", False):
                with patch("rundeck_exporter.metrics_collector.cached_request", side_effect=side_effect):
                    return collector._get_project_executions(project)
    return _run


@pytest.fixture
def mock_collect(collector):
    """Returns a context manager that patches both request functions and optionally patches collector.args attributes."""
    @contextmanager
    def _ctx(side_effect, **arg_overrides):
        request_patches = [
            patch("rundeck_exporter.metrics_collector.request", side_effect=side_effect),
            patch("rundeck_exporter.metrics_collector.cached_request", side_effect=side_effect),
        ]
        arg_patches = [patch.object(collector.args, k, v) for k, v in arg_overrides.items()]
        with ExitStack() as stack:
            for p in request_patches + arg_patches:
                stack.enter_context(p)
            yield
    return _ctx
