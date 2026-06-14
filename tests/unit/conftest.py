from contextlib import ExitStack, contextmanager
from unittest.mock import patch

import pytest
from prometheus_client import REGISTRY

from rundeck_exporter.metrics_collector import RundeckMetricsCollector


@pytest.fixture(scope="module")
def collector():
    """
    Provide a RundeckMetricsCollector instance registered with the Prometheus registry.
    
    The collector is registered for the duration of the fixture and automatically unregistered and shut down during cleanup.
    
    Yields:
        RundeckMetricsCollector: A metrics collector instance for testing.
    """
    c = RundeckMetricsCollector()
    REGISTRY.register(c)
    try:
        yield c
    finally:
        REGISTRY.unregister(c)
        c.executor.shutdown(wait=True)


@pytest.fixture
def run_project_executions(collector):
    """
    Provide a factory function to test project executions retrieval with mock HTTP responses.
    """
    def _run(side_effect, project=None):
        """
        Retrieve project executions with controlled request behavior.
        
        Parameters:
            side_effect: Behavior for mocked request functions (return value or exception to simulate).
            project (dict, optional): Project configuration dict. Defaults to {"name": "test1"}.
        
        Returns:
            The result of collector._get_project_executions.
        """
        project = project or {"name": "test1"}
        with patch("rundeck_exporter.metrics_collector.request", side_effect=side_effect):
            with patch.object(collector.args, "rundeck_projects_executions_cache", False):
                with patch("rundeck_exporter.metrics_collector.cached_request", side_effect=side_effect):
                    return collector._get_project_executions(project)
    return _run


@pytest.fixture
def mock_collect(collector):
    """
    Return a context manager factory for patching HTTP requests and collector configuration.
    
    The factory patches both request and cached_request functions with a given side_effect
    and optionally overrides collector.args attributes.
    """
    @contextmanager
    def _ctx(side_effect, **arg_overrides):
        """
        Context manager that patches request functions and collector configuration.
        
        Patches `rundeck_exporter.metrics_collector.request` and
        `rundeck_exporter.metrics_collector.cached_request` with the given `side_effect`,
        and patches attributes on `collector.args` according to `arg_overrides`.
        
        Parameters:
            side_effect: Behavior to apply to patched request functions.
            **arg_overrides: Attributes to patch on `collector.args`.
        """
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
