import pytest


def _names(metrics):
    return [m.name for m in metrics]


def _values(metrics):
    return {m.name: m.samples[0].value for m in metrics if m.samples}


def _by_name(metrics):
    return {m.name: m for m in metrics}


class TestGetCounters:
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
        metrics = {"gauges": {"rundeck_runningExecutions": {"value": value}}}
        assert _values(list(collector._get_counters(metrics)))["rundeck_runningExecutions"] == expected

    def test_meter_rate_fields_excluded(self, collector):
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
