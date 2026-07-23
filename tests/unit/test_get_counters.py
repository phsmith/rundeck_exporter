"""Tests for RundeckMetricsCollector._get_counters() (legacy Dropwizard metrics format)."""

import pytest


def _names(metrics):
    """
    Extract the name of each metric.
    
    Parameters:
    	metrics: An iterable of metric objects, each with a name attribute.
    
    Returns:
    	list: A list of metric names.
    """
    return [m.name for m in metrics]


def _values(metrics):
    """
    Build a mapping from metric names to their first sample values.
    
    Only metrics with at least one sample are included in the result.
    
    Returns:
        A dictionary mapping metric names to their first sample values.
    """
    return {m.name: m.samples[0].value for m in metrics if m.samples}


def _by_name(metrics):
    """
    Build a mapping of metric names to metric objects.
    
    Parameters:
    	metrics (iterable): Collection of metric objects with a name attribute
    
    Returns:
    	dict: Dictionary mapping metric names to metric objects
    """
    return {m.name: m for m in metrics}


class TestGetCounters:
    """Verifies name filtering/normalization and per-metric-type conversion to Prometheus families."""

    @pytest.mark.parametrize("counter_name,expected_names", [
        pytest.param("rundeck_execution_status_total", [], id="excluded-prefix"),
        pytest.param("rundeck_http_status_count", ["rundeck_http_status_count"], id="status-in-middle-kept"),
        pytest.param("rundeck_rateLimiter_count", ["rundeck_rateLimiter_count"], id="rate-in-name-kept"),
    ])
    def test_counter_name_filtering(self, collector, counter_name, expected_names):
        """Exclusion applies only to the rundeck_execution_status_* prefix, not to names merely containing 'status' or 'rate'."""
        metrics = {"counters": {counter_name: {"count": 5}}}
        assert _names(list(collector._get_counters(metrics))) == expected_names

    @pytest.mark.parametrize("counter_name,expected_name", [
        pytest.param("myMetric", "rundeck_myMetric", id="rundeck-prefix-added"),
        pytest.param("my-metric.count", "rundeck_my_metric_count", id="dash-dot-sanitized"),
    ])
    def test_counter_name_normalization(self, collector, counter_name, expected_name):
        """Counter names without the rundeck_ prefix get it added; dashes and dots are sanitized to underscores."""
        metrics = {"counters": {counter_name: {"count": 1}}}
        assert _names(list(collector._get_counters(metrics))) == [expected_name]

    @pytest.mark.parametrize("value,expected", [
        pytest.param(None, 0.0, id="none-becomes-zero"),
        pytest.param(42, 42.0, id="numeric-passthrough"),
    ])
    def test_gauge_value_emits_correctly(self, collector, value, expected):
        """A gauge's null value must be emitted as 0.0; numeric values pass through unchanged."""
        metrics = {"gauges": {"rundeck_runningExecutions": {"value": value}}}
        assert _values(list(collector._get_counters(metrics)))["rundeck_runningExecutions"] == expected

    def test_meter_rate_fields_excluded(self, collector):
        """Meter rate subfields (oneMinuteRate, etc.) must not be emitted as their own metrics."""
        metrics = {
            "meters": {
                "rundeck_someMeter": {
                    "count": 10,
                    "oneMinuteRate": 0.5,
                    "fiveMinuteRate": 0.3,
                    "fifteenMinuteRate": 0.1,
                    "meanRate": 0.4,
                }
            }
        }
        # count is the only non-rate field; emitted as a counter named after the meter.
        assert _names(list(collector._get_counters(metrics))) == ["rundeck_someMeter"]

    def test_meter_bool_values_excluded(self, collector):
        """Boolean meter subfields must be excluded (bool is an int subclass and would otherwise pass the numeric check)."""
        metrics = {"meters": {"rundeck_someMeter": {"count": 5, "active": True}}}
        assert _names(list(collector._get_counters(metrics))) == ["rundeck_someMeter"]

    def test_meter_count_is_counter_exposed_as_total(self, collector):
        """The Dropwizard count field must stay a counter, exposed as {name}_total — not a gauge."""
        metrics = {"meters": {"rundeck_someMeter": {"count": 10}}}
        families = _by_name(list(collector._get_counters(metrics)))
        assert families["rundeck_someMeter"].type == "counter"
        sample_names = {s.name for s in families["rundeck_someMeter"].samples}
        assert "rundeck_someMeter_total" in sample_names

    def test_timer_yields_all_numeric_non_rate_subfields(self, collector):
        """A timer's count becomes a counter; its distribution stats become separate gauges, rates excluded."""
        metrics = {
            "timers": {
                "rundeck_someTimer": {
                    "count": 100,
                    "mean": 0.05,
                    "max": 0.2,
                    "min": 0.01,
                    "p99": 0.19,
                    "oneMinuteRate": 1.0,
                }
            }
        }
        families = _by_name(list(collector._get_counters(metrics)))
        names = set(families)
        # count → counter named after the timer; distribution stats → gauges with _stat suffix.
        assert {"rundeck_someTimer", "rundeck_someTimer_mean", "rundeck_someTimer_max",
                "rundeck_someTimer_min", "rundeck_someTimer_p99"} <= names
        assert not any("Rate" in n for n in names)
        assert families["rundeck_someTimer"].type == "counter"
        for stat in ("mean", "max", "min", "p99"):
            assert families[f"rundeck_someTimer_{stat}"].type == "gauge"
