from unittest.mock import patch

import pytest


SYSTEM_INFO = {
    "system": {
        "stats": {
            "uptime": {"duration": 12345, "since": {"epoch": 1_000_000_000, "unit": "ms"}},
            "cpu": {"loadAverage": {"average": 0.42}},
            "memory": {"free": 512, "total": 1024, "max": 2048},
            "scheduler": {"running": 3, "threadPoolSize": 10},
            "threads": {"active": 7},
        }
    }
}

def _stat_names(collector, cpu=True, memory=True):
    with patch.object(collector.args, "rundeck_cpu_stats", cpu):
        with patch.object(collector.args, "rundeck_memory_stats", memory):
            return {m.name for m in collector._get_system_stats(SYSTEM_INFO)}


class TestGetSystemStats:
    def test_yields_one_family_per_stat_counter_pair(self, collector):
        """Each stat/counter pair must produce a distinct named GaugeMetricFamily."""
        with patch.object(collector.args, "rundeck_cpu_stats", True):
            with patch.object(collector.args, "rundeck_memory_stats", True):
                result = list(collector._get_system_stats(SYSTEM_INFO))

        # uptime.since, cpu.loadAverage_ratio, memory.free/total/max, scheduler.running/threadPoolSize, threads.active
        names = [m.name for m in result]
        assert len(names) == len(set(names)), "each family must have a unique name"
        assert len(result) == 8

    def test_metric_names_encode_stat_and_counter(self, collector):
        names = _stat_names(collector)
        assert {
            "rundeck_system_stats_threads_active",
            "rundeck_system_stats_scheduler_running",
            "rundeck_system_stats_scheduler_threadPoolSize",
            "rundeck_system_stats_uptime_since",
            "rundeck_system_stats_cpu_loadAverage_ratio",
            "rundeck_system_stats_memory_free_bytes",
        } <= names

    @pytest.mark.parametrize("cpu,memory,excluded", [
        pytest.param(False, True, "_cpu_", id="cpu-flag-off"),
        pytest.param(True, False, "_memory_", id="memory-flag-off"),
    ])
    def test_stat_excluded_when_flag_off(self, collector, cpu, memory, excluded):
        names = _stat_names(collector, cpu=cpu, memory=memory)
        assert not any(excluded in n for n in names)

    def test_unit_and_duration_counters_skipped(self, collector):
        names = _stat_names(collector)
        assert not any(n.endswith("_unit") or n.endswith("_duration") for n in names)

    def test_uptime_since_uses_epoch_value(self, collector):
        families = {m.name: m for m in collector._get_system_stats(SYSTEM_INFO)}
        assert families["rundeck_system_stats_uptime_since"].samples[0].value == 1_000_000_000
