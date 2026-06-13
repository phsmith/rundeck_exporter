import atexit
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from urllib.parse import urlparse

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY, CounterMetricFamily, GaugeMetricFamily, InfoMetricFamily
from prometheus_client.registry import Collector

from rundeck_exporter.args import rundeck_exporter_args
from rundeck_exporter.constants import RUNDECK_EXECUTION_STATUSES, RUNDECK_USERPASSWORD
from rundeck_exporter.utils import cached_request, exit_with_msg, logging, request

_SANITIZE_RE = re.compile(r"[-.]")


class RundeckProjectExecution(Enum):
    """Class for mapping Rundeck projects execution attributes"""

    START = 1
    DURATION = 2
    STATUS = 3


@dataclass
class RundeckProjectExecutionRecord:
    """Class for keeping track of Rundeck projects execution info"""

    labels_value: list[str]
    value: float
    execution_type: RundeckProjectExecution


class RundeckMetricsCollector(Collector):
    """Class for collect Rundeck metrics"""

    def __init__(self):
        self.args = rundeck_exporter_args
        parsed = urlparse(self.args.rundeck_url)
        instance_address = parsed.netloc
        if not instance_address:
            exit_with_msg(
                msg=f"Could not determine host from rundeck_url: {self.args.rundeck_url!r}",
                level="critical",
            )
        self.instance_address = instance_address
        self.default_labels = ["instance_address"]
        self.default_labels_values = [self.instance_address]
        self.default_project_executions_labels = self.default_labels + [
            "project_name",
            "job_id",
            "job_name",
            "job_group",
            "job_options",
            "execution_id",
            "execution_type",
            "user",
        ]
        self.executor = ThreadPoolExecutor(
            thread_name_prefix="rundeck_exporter", max_workers=self.args.threadpool_max_workers
        )
        atexit.register(self.executor.shutdown)
        self._execution_scrape_lock = threading.Lock()

    def describe(self):
        return []

    def _fetch(self, endpoint: str) -> dict | list | None:
        if self.args.rundeck_projects_executions_cache:
            return cached_request(endpoint)
        return request(endpoint)

    def _get_project_executions(self, project: dict) -> tuple[list, dict]:
        """
        Method to get Rundeck projects executions info
        """

        project_name = project["name"]
        project_execution_records: list[RundeckProjectExecutionRecord] = []
        project_executions_limit = self.args.rundeck_projects_executions_limit
        project_executions_filter = self.args.rundeck_project_executions_filter
        project_executions_total = {"project": project_name, "total_executions": 0}
        endpoint_executions = f"/project/{project_name}/executions?recentFilter={project_executions_filter}&max={project_executions_limit}"
        endpoint_executions_running = f"/project/{project_name}/executions/running?max={project_executions_limit}"
        endpoint_executions_metrics = f"/project/{project_name}/executions/metrics?recentFilter=1d"

        try:
            # running endpoint always fetched fresh — "currently running" is real-time state
            project_executions_running_info = request(endpoint_executions_running)
            project_executions_info = self._fetch(endpoint_executions)
            project_executions_total_info = self._fetch(endpoint_executions_metrics)

            if (
                not project_executions_running_info
                or not project_executions_info
                or not project_executions_total_info
                or not isinstance(project_executions_running_info, dict)
                or not isinstance(project_executions_info, dict)
                or not isinstance(project_executions_total_info, dict)
            ):
                return project_execution_records, project_executions_total

            project_executions_running_info_list = project_executions_running_info.get("executions", [])
            # /executions/metrics?recentFilter=1d total counts only completed executions;
            # add the running list to include in-progress executions in the total.
            project_executions_total["total_executions"] = project_executions_total_info["total"] + len(
                project_executions_running_info_list
            )

            # Deduplicate by execution id — running executions can also appear in the recent filter list
            seen_ids: set = set()
            merged = project_executions_running_info_list + project_executions_info.get("executions", [])
            project_executions = []
            for execution in merged:
                execution_id = execution.get("id")
                if execution_id not in seen_ids:
                    seen_ids.add(execution_id)
                    project_executions.append(execution)

            for project_execution in project_executions:
                job_info = project_execution.get("job", {})
                job_id = job_info.get("id") or ""
                job_name = job_info.get("name") or ""
                job_group = job_info.get("group") or ""
                if self.args.rundeck_projects_executions_include_job_options:
                    job_options = ",".join(job_info.get("options", {}).keys())
                else:
                    job_options = ""
                execution_id = str(project_execution.get("id") or "")
                execution_type = project_execution.get("executionType") or ""
                user = project_execution.get("user") or ""

                project_executions_labels_value = self.default_labels_values + [
                    project_name,
                    job_id,
                    job_name,
                    job_group,
                    job_options,
                    execution_id,
                    execution_type,
                    user,
                ]

                # STATUS is emitted for every execution regardless of whether date-started is present
                for status in RUNDECK_EXECUTION_STATUSES:
                    value = 1 if project_execution.get("status", "unknown") == status else 0
                    project_execution_records.append(
                        RundeckProjectExecutionRecord(
                            project_executions_labels_value + [status], value, RundeckProjectExecution.STATUS
                        )
                    )

                # START and DURATION require a timestamp; skip if Rundeck hasn't stamped date-started yet
                date_started = project_execution.get("date-started") or {}
                if not date_started:
                    continue

                # Rundeck unixtime is in milliseconds; job_start_time kept in ms (historical behavior)
                job_start_time = date_started.get("unixtime", 0)
                job_end_time = (project_execution.get("date-ended") or {}).get("unixtime", datetime.now().timestamp() * 1000)
                job_execution_duration = (job_end_time - job_start_time) / 1000

                project_execution_records.append(
                    RundeckProjectExecutionRecord(
                        project_executions_labels_value, job_start_time, RundeckProjectExecution.START
                    )
                )
                project_execution_records.append(
                    RundeckProjectExecutionRecord(
                        project_executions_labels_value, job_execution_duration, RundeckProjectExecution.DURATION
                    )
                )
        except Exception as error:  # nosec
            logging.error(error)

        return project_execution_records, project_executions_total

    def _get_project_nodes(self, project: dict) -> dict:
        """
        Method to get Rundeck projects nodes info
        """

        project_name = project["name"]
        endpoint = f"/project/{project_name}/resources"
        project_nodes = self._fetch(endpoint)
        if not project_nodes or not isinstance(project_nodes, dict):
            return {}
        return {project_name: len(project_nodes)}

    def _get_system_stats(self, system_info: dict):
        """
        Method to get Rundeck system stats
        """

        for stat, stat_values in system_info["system"]["stats"].items():
            for counter, value in stat_values.items():
                if counter in ["unit", "duration"]:
                    continue
                elif stat == "uptime" and counter == "since":
                    value = value["epoch"]
                elif stat == "cpu":
                    if self.args.rundeck_cpu_stats and isinstance(value, dict):
                        counter = f"{counter}_ratio"
                        value = value["average"]
                    else:
                        continue
                elif stat == "memory":
                    if self.args.rundeck_memory_stats:
                        counter = f"{counter}_bytes"
                    else:
                        continue

                rundeck_system_stats = GaugeMetricFamily(
                    name=f"rundeck_system_stats_{stat}_{counter}",
                    documentation="Rundeck system stats",
                    labels=self.default_labels,
                )
                rundeck_system_stats.add_metric(self.default_labels_values, value)
                yield rundeck_system_stats

    def _get_counters(self, metrics: dict):
        """
        Method to get Rundeck metrics counters, gauges and timers
        """

        for metric, metric_value in metrics.items():
            if not isinstance(metric_value, dict):
                continue

            for counter_name, counter_value in metric_value.items():
                counter_name = _SANITIZE_RE.sub("_", counter_name)

                if not counter_name.startswith("rundeck"):
                    counter_name = "rundeck_" + counter_name

                # Exclude rundeck_execution_status_* counters — those are emitted as
                # one-hot gauge labels in _get_project_executions, not here.
                if metric == "counters" and not counter_name.startswith("rundeck_execution_status"):
                    if isinstance(counter_value, dict) and "count" in counter_value:
                        # Dropwizard Counter is an up/down counter (can decrement) → gauge, not counter
                        gauge = GaugeMetricFamily(
                            name=counter_name,
                            documentation="Rundeck counters metrics",
                            labels=self.default_labels,
                        )
                        gauge.add_metric(self.default_labels_values, counter_value["count"])
                        yield gauge

                elif metric == "gauges":
                    if isinstance(counter_value, dict) and "value" in counter_value:
                        value = counter_value["value"]
                        gauge = GaugeMetricFamily(
                            name=counter_name,
                            documentation="Rundeck gauges metrics",
                            labels=self.default_labels,
                        )
                        gauge.add_metric(self.default_labels_values, value if value is not None else 0)
                        yield gauge

                elif metric in ("meters", "timers"):
                    if isinstance(counter_value, dict):
                        for stat, value in counter_value.items():
                            if not isinstance(value, (int, float)) or isinstance(value, bool) or "rate" in stat.lower():
                                continue
                            if stat == "count":
                                # Dropwizard meter/timer count is a monotonic event total → counter,
                                # exposed as {counter_name}_total
                                family = CounterMetricFamily(
                                    name=counter_name,
                                    documentation=f"Rundeck {metric} metrics",
                                    labels=self.default_labels,
                                )
                            else:
                                # snapshot distribution stat (min/max/mean/p95/…) → gauge
                                family = GaugeMetricFamily(
                                    name=f"{counter_name}_{_SANITIZE_RE.sub('_', stat)}",
                                    documentation=f"Rundeck {metric} metrics",
                                    labels=self.default_labels,
                                )
                            family.add_metric(self.default_labels_values, value)
                            yield family

    def collect(self):
        """
        Method to collect Rundeck metrics
        """

        scrape_start = time.perf_counter()

        def _scrape_duration():
            m = GaugeMetricFamily(
                "rundeck_exporter_scrape_duration_seconds",
                "Duration of the last Rundeck scrape in seconds",
            )
            m.add_metric([], time.perf_counter() - scrape_start)
            return m

        try:
            # Rundeck system info
            metrics = request("/metrics/metrics")
            system_info = request("/system/info")

            if not metrics or not system_info or not isinstance(metrics, dict) or not isinstance(system_info, dict):
                return

            execution_mode = system_info["system"].get("executions", {}).get("executionMode")
            rundeck_system_info = InfoMetricFamily(
                name="rundeck_system", documentation="Rundeck system info", labels=self.default_labels
            )
            rundeck_system_info.add_metric(
                self.default_labels_values, {x: str(y) for x, y in system_info["system"]["rundeck"].items()}
            )

            logging.debug(f"Rundeck execution mode: {execution_mode}.")

            if self.args.no_checks_in_passive_mode and execution_mode == "passive":
                return

            rundeck_execution_mode_active = GaugeMetricFamily(
                "rundeck_execution_mode_active", "Rundeck Active Execution Mode Status", labels=self.default_labels
            )
            rundeck_execution_mode_passive = GaugeMetricFamily(
                "rundeck_execution_mode_passive", "Rundeck Passive Execution Mode Status", labels=self.default_labels
            )

            if execution_mode == "passive":
                rundeck_execution_mode_active.add_metric(self.default_labels_values, 0)
                rundeck_execution_mode_passive.add_metric(self.default_labels_values, 1)
            else:
                rundeck_execution_mode_active.add_metric(self.default_labels_values, 1)
                rundeck_execution_mode_passive.add_metric(self.default_labels_values, 0)

            yield rundeck_system_info
            yield rundeck_execution_mode_active
            yield rundeck_execution_mode_passive

            # Rundeck system stats
            for system_stats in self._get_system_stats(system_info):
                yield system_stats

            # Rundeck counters
            if self.args.rundeck_api_version < 25 and not (self.args.rundeck_username and RUNDECK_USERPASSWORD):
                logging.warning(
                    f'Unsupported API version "{self.args.rundeck_api_version}"'
                    + f" for API request: /api/{self.args.rundeck_api_version}/metrics/metrics."
                    + " Minimum supported version is 25."
                    + " Some metrics like rundeck_scheduler_quartz_* will not be available."
                    + " Use Username and Password options to get the metrics."
                )
            else:
                for counters in self._get_counters(metrics):
                    yield counters

            # Rundeck projects executions info
            if self.args.rundeck_projects_executions:
                endpoint = "/projects"

                if self.args.rundeck_projects_filter:
                    projects = [{"name": x} for x in self.args.rundeck_projects_filter]
                else:
                    projects = self._fetch(endpoint)

                    if not projects:
                        return

                if self._execution_scrape_lock.acquire(blocking=False):
                    try:
                        project_execution_records = list(self.executor.map(self._get_project_executions, projects))
                    finally:
                        self._execution_scrape_lock.release()
                else:
                    logging.warning("Previous scrape still in progress; skipping project execution fetch.")
                    project_execution_records = []

                project_start_metrics = GaugeMetricFamily(
                    "rundeck_project_start_timestamp",
                    "Rundeck Project Start Timestamp",
                    labels=self.default_project_executions_labels,
                )
                project_duration_metrics = GaugeMetricFamily(
                    "rundeck_project_execution_duration_seconds",
                    "Rundeck Project Execution Duration",
                    labels=self.default_project_executions_labels,
                )
                project_metrics = GaugeMetricFamily(
                    "rundeck_project_execution_status",
                    "Rundeck Project Execution Status",
                    labels=self.default_project_executions_labels + ["status"],
                )
                project_executions_metrics = GaugeMetricFamily(
                    "rundeck_project_executions",
                    "Rundeck Project Executions (sliding 1d window, non-monotonic gauge)",
                    labels=self.default_labels + ["project_name"],
                )

                for project_execution_record_group, project_executions_total in project_execution_records:
                    timestamp = datetime.now().timestamp()
                    project_executions_metrics.add_metric(
                        self.default_labels_values + [project_executions_total["project"]],
                        project_executions_total["total_executions"],
                        timestamp=timestamp,
                    )
                    for project_execution_record in project_execution_record_group:
                        if project_execution_record.execution_type == RundeckProjectExecution.START:
                            project_start_metrics.add_metric(
                                project_execution_record.labels_value,
                                project_execution_record.value,
                                timestamp=timestamp,
                            )
                        elif project_execution_record.execution_type == RundeckProjectExecution.DURATION:
                            project_duration_metrics.add_metric(
                                project_execution_record.labels_value,
                                project_execution_record.value,
                                timestamp=timestamp,
                            )
                        elif project_execution_record.execution_type == RundeckProjectExecution.STATUS:
                            project_metrics.add_metric(
                                project_execution_record.labels_value,
                                project_execution_record.value,
                                timestamp=timestamp,
                            )

                yield project_start_metrics
                yield project_duration_metrics
                yield project_metrics
                yield project_executions_metrics

                if self.args.rundeck_projects_nodes_info:
                    project_nodes_records = list(self.executor.map(self._get_project_nodes, projects))
                    project_nodes_total = GaugeMetricFamily(
                        name="rundeck_project_nodes_total",
                        documentation="Rundeck project nodes total",
                        labels=self.default_labels + ["project_name"],
                    )
                    for project_nodes in project_nodes_records:
                        for project, count in project_nodes.items():
                            project_nodes_total.add_metric(self.default_labels_values + [project], count)
                    yield project_nodes_total

        finally:
            yield _scrape_duration()

    def run(self) -> None:
        try:
            REGISTRY.register(self)

            logging.info(f"Rundeck exporter server started at {self.args.host}:{self.args.port}...")
            start_http_server(self.args.port, addr=self.args.host, registry=REGISTRY)

            while True:
                time.sleep(1)
        except OSError as os_error:
            exit_with_msg(msg=str(os_error), level="critical")
