import pytest


def _names(metrics):
    return [m.name for m in metrics]


def _values(metrics):
    return {m.name: m.samples[0].value for m in metrics if m.samples}


def _by_name(metrics):
    return {m.name: m for m in metrics}


class TestGetCounters:
    def test_excluded_counter_produces_no_metrics(self, collector):
        metrics = {"counters": {"rundeck_execution_status_total": {"count": 5}}}
        assert _names(list(collector._get_counters(metrics))) == []

    def test_counter_with_status_in_middle_not_excluded(self, collector):
        """Only rundeck_execution_status_* prefix is excluded — not any name containing 'status'."""
        metrics = {"counters": {"rundeck_http_status_count": {"count": 3}}}
        assert _names(list(collector._get_counters(metrics))) == ["rundeck_http_status_count"]

    def test_counter_name_containing_rate_emitted(self, collector):
        """A counter whose base name contains 'rate' must NOT be dropped — only rate sub-fields are filtered."""
        metrics = {"counters": {"rundeck_rateLimiter_count": {"count": 1}}}
        assert _names(list(collector._get_counters(metrics))) == ["rundeck_rateLimiter_count"]

    def test_counter_prefixed_with_rundeck(self, collector):
        metrics = {"counters": {"myMetric": {"count": 7}}}
        assert _names(list(collector._get_counters(metrics))) == ["rundeck_myMetric"]

    def test_dash_and_dot_sanitized_to_underscore(self, collector):
        metrics = {"counters": {"my-metric.count": {"count": 1}}}
        assert _names(list(collector._get_counters(metrics))) == ["rundeck_my_metric_count"]

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
