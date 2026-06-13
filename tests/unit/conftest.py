import pytest

from rundeck_exporter.metrics_collector import RundeckMetricsCollector


@pytest.fixture()
def collector():
    c = RundeckMetricsCollector()
    yield c
    c.executor.shutdown(wait=False)
