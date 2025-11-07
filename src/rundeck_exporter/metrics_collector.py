import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from enum import Enum
from time import sleep

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY, CounterMetricFamily, GaugeMetricFamily, InfoMetricFamily

from rundeck_exporter.args import rundeck_exporter_args
from rundeck_exporter.constants import RUNDECK_USERPASSWORD
from rundeck_exporter.utils import cached_request, exit_with_msg, logging, request


class RundeckProjectExecution(Enum):
    """Class for mapping Rundeck projects execution attributes"""

    START = 1
    DURATION = 2
    STATUS = 3


class RundeckProjectExecutionRecord:
    """Class for keeping track of Rundeck projects execution info"""

    def __init__(self, tags: list, value: float, execution_type: RundeckProjectExecution):
        self.tags = tags
        self.value = value
        self.execution_type = execution_type


class RundeckMetricsCollector:
    """Class for collect Rundeck metrics"""

    def __init__(self):
        self.args = rundeck_exporter_args.namespace
        self.instance_address = re.findall(r"https?://([\w\d:._-]+)", self.args.rundeck_url)[0]
        self.default_labels = ["instance_address"]
        self.default_labels_values = [self.instance_address]

    def get_project_executions(self, project: dict):
        """
        Method to get Rundeck projects executions info
        """

        project_name = project["name"]
        project_execution_records = list()
        project_executions_limit = self.args.rundeck_projects_executions_limit
        project_executions_filter = self.args.rundeck_project_executions_filter
        project_executions_total = {"project": project_name, "total_executions": 0}
        endpoint_executions = f"/project/{project_name}/executions?recentFilter={project_executions_filter}&max={project_executions_limit}"
        endpoint_executions_running = f"/project/{project_name}/executions/running?max={project_executions_limit}"
        endpoint_executions_metrics = f"/project/{project_name}/executions/metrics?recentFilter=1d"

        try:
            if self.args.rundeck_projects_executions_cache:
                project_executions_running_info = cached_request(endpoint_executions_running)
                project_executions_info = cached_request(endpoint_executions)
                project_executions_total_info = cached_request(endpoint_executions_metrics)
            else:
                project_executions_running_info = request(endpoint_executions_running)
                project_executions_info = request(endpoint_executions)
                project_executions_total_info = request(endpoint_executions_metrics)

            project_executions_running_info_list = project_executions_running_info.get("executions", [])
            project_executions_total["total_executions"] = project_executions_total_info["total"] + len(
                project_executions_running_info_list
            )
            project_executions = project_executions_running_info_list + project_executions_info.get("executions", [])

            for project_execution in project_executions:
                job_info = project_execution.get("job", {})
                job_id = job_info.get("id", "None")
                job_name = job_info.get("name", "None")
                job_group = job_info.get("group", "None")
                execution_id = str(project_execution.get("id", "None"))
                execution_type = project_execution.get("executionType")
                user = project_execution.get("user")
                default_metrics = self.default_labels_values + [
                    project_name,
                    job_id,
                    job_name,
                    job_group,
                    execution_id,
                    execution_type,
                    user,
                ]

                # Job start/end times
                timestamp_now = datetime.now().timestamp() * 1000
                job_start_time = project_execution.get("date-started", {}).get("unixtime", 0)
                job_end_time = project_execution.get("date-ended", {}).get("unixtime", timestamp_now)
                job_execution_duration = (job_end_time - job_start_time) / 1000

                project_execution_records.append(
                    RundeckProjectExecutionRecord(default_metrics, job_start_time, RundeckProjectExecution.START)
                )
                project_execution_records.append(
                    RundeckProjectExecutionRecord(
                        default_metrics, job_execution_duration, RundeckProjectExecution.DURATION
                    )
                )

                for status in ["succeeded", "running", "failed", "aborted", "unknown"]:
                    value = 0

                    if project_execution.get("status", "unknown") == status:
                        value = 1

                    project_execution_records.append(
                        RundeckProjectExecutionRecord(default_metrics + [status], value, RundeckProjectExecution.STATUS)
                    )

        except Exception as error:  # nosec
            logging.error(error)

        return project_execution_records, project_executions_total

    def get_project_nodes(self, project: dict):
        """
        Method to get Rundeck projects nodes info
        """

        project_nodes = dict()
        project_name = project["name"]
        endpoint = f"/project/{project_name}/resources"
        project_nodes = cached_request(endpoint)
        project_nodes_info = {project["name"]: list(project_nodes.values())}

        return project_nodes_info

    def get_system_stats(self, system_info: dict):
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

    def get_counters(self, metrics: dict):
        """
        Method to get Rundeck metrics counters, gauges and timers
        """

        for metric, metric_value in metrics.items():
            if not isinstance(metric_value, dict):
                continue

            for counter_name, counter_value in metric_value.items():
                counter_name = re.sub(r"[-.]", "_", counter_name)

                rundeck_meters_timers = CounterMetricFamily(
                    name=counter_name, documentation=f"Rundeck {metric} metrics", labels=self.default_labels
                )
                rundeck_counters = GaugeMetricFamily(
                    name=counter_name, documentation="Rundeck counters metrics", labels=self.default_labels
                )
                rundeck_gauges = GaugeMetricFamily(
                    name=counter_name, documentation="Rundeck gauges metrics", labels=self.default_labels
                )

                if "rate" in counter_name.lower():
                    continue

                if not counter_name.startswith("rundeck"):
                    counter_name = "rundeck_" + counter_name

                if metric == "counters" and "status" not in counter_name:
                    if isinstance(counter_value, dict) and "count" in counter_value:
                        counter_value = counter_value["count"]
                        rundeck_counters.add_metric(self.default_labels_values, counter_value)
                        yield rundeck_counters
                    else:
                        # Skip if it's not a proper counter structure
                        continue

                elif metric == "gauges":
                    if isinstance(counter_value, dict) and "value" in counter_value:
                        counter_value = counter_value["value"]
                    else:
                        # Skip if it's not a proper gauge structure
                        continue

                    if "services" in counter_name:
                        services_trackers = rundeck_gauges
                    else:
                        services_trackers = rundeck_counters

                    if counter_value is not None:
                        services_trackers.add_metric(self.default_labels_values, counter_value)
                    else:
                        services_trackers.add_metric(self.default_labels_values, 0)

                    yield services_trackers

                elif metric == "meters" or metric == "timers":
                    if isinstance(counter_value, dict):
                        for counter, value in counter_value.items():
                            if counter == "count" and not isinstance(value, str) and isinstance(value, (int, float)):
                                rundeck_meters_timers.add_metric(self.default_labels_values, value)
                                yield rundeck_meters_timers
                    else:
                        # Skip if it's not a proper meters/timers structure
                        continue

    def collect(self):
        """
        Method to collect Rundeck metrics
        """

        # Rundeck system info
        metrics = request("/metrics/metrics")
        system_info = request("/system/info")

        if not metrics or not system_info:
            return

        api_version = int(system_info["system"]["rundeck"]["apiversion"])
        execution_mode = system_info["system"].get("executions", {}).get("executionMode")
        rundeck_system_info = InfoMetricFamily(
            name="rundeck_system", documentation="Rundeck system info", labels=self.default_labels
        )
        rundeck_system_info.add_metric(
            self.default_labels_values, {x: str(y) for x, y in system_info["system"]["rundeck"].items()}
        )

        # Rundeck server execution mode
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
        for system_stats in self.get_system_stats(system_info):
            yield system_stats

        # Rundeck counters
        if api_version >= self.args.rundeck_api_version < 25 and not (
            self.args.rundeck_username and RUNDECK_USERPASSWORD
        ):
            logging.warning(
                f'Unsupported API version "{self.args.rundeck_api_version}"'
                + f" for API request: /api/{self.args.rundeck_api_version}/metrics/metrics."
                + " Minimum supported version is 25."
                + " Some metrics like rundeck_scheduler_quartz_* will not be available."
                + " Use Username and Password options to get the metrics."
            )
        else:
            for counters in self.get_counters(metrics):
                yield counters

        # Rundeck projects executions info
        rundeck_projects_filter = self.args.rundeck_projects_filter

        if self.args.rundeck_projects_executions:
            endpoint = "/projects"

            if rundeck_projects_filter:
                if isinstance(rundeck_projects_filter, str):
                    rundeck_projects_filter = rundeck_projects_filter.split()

                projects = [{"name": x} for x in rundeck_projects_filter]
            else:
                if self.args.rundeck_projects_executions_cache:
                    projects = cached_request(endpoint)
                else:
                    projects = request(endpoint)

            with ThreadPoolExecutor(
                thread_name_prefix="project_executions", max_workers=self.args.threadpool_max_workers
            ) as project_executions_threadpool:
                project_execution_records = project_executions_threadpool.map(self.get_project_executions, projects)
                timestamp = datetime.now().timestamp()

                default_labels = self.default_labels + [
                    "project_name",
                    "job_id",
                    "job_name",
                    "job_group",
                    "execution_id",
                    "execution_type",
                    "user",
                ]

                project_start_metrics = GaugeMetricFamily(
                    "rundeck_project_start_timestamp",
                    "Rundeck Project ProjectName Start Timestamp",
                    labels=default_labels,
                )

                project_duration_metrics = GaugeMetricFamily(
                    "rundeck_project_execution_duration_seconds",
                    "Rundeck Project ProjectName Execution Duration",
                    labels=default_labels,
                )

                project_metrics = GaugeMetricFamily(
                    "rundeck_project_execution_status",
                    "Rundeck Project ProjectName Execution Status",
                    labels=default_labels + ["status"],
                )

                project_executions_total_metrics = CounterMetricFamily(
                    "rundeck_project_executions_total",
                    "Rundeck Project ProjectName Total Executions",
                    labels=self.default_labels + ["project_name"],
                )

                for project_execution_record_group, project_executions_total in project_execution_records:
                    project_executions_total_metrics.add_metric(
                        self.default_labels_values + [project_executions_total["project"]],
                        project_executions_total["total_executions"],
                        timestamp=timestamp,
                    )
                    for project_execution_record in project_execution_record_group:
                        if project_execution_record.execution_type == RundeckProjectExecution.START:
                            project_start_metrics.add_metric(
                                project_execution_record.tags, project_execution_record.value, timestamp=timestamp
                            )
                        elif project_execution_record.execution_type == RundeckProjectExecution.DURATION:
                            project_duration_metrics.add_metric(
                                project_execution_record.tags, project_execution_record.value, timestamp=timestamp
                            )
                        elif project_execution_record.execution_type == RundeckProjectExecution.STATUS:
                            project_metrics.add_metric(
                                project_execution_record.tags, project_execution_record.value, timestamp=timestamp
                            )

                yield project_start_metrics
                yield project_duration_metrics
                yield project_metrics
                yield project_executions_total_metrics

            if self.args.rundeck_projects_nodes_info:
                with ThreadPoolExecutor(
                    thread_name_prefix="project_nodes", max_workers=self.args.threadpool_max_workers
                ) as project_nodes_threadpool:
                    project_nodes_records = project_nodes_threadpool.map(self.get_project_nodes, projects)
                    project_nodes_total = GaugeMetricFamily(
                        name="rundeck_project_nodes_total",
                        documentation="Rundeck project nodes total",
                        labels=self.default_labels + ["project_name"],
                    )

                    for project_nodes in project_nodes_records:
                        for project, nodes in project_nodes.items():
                            project_nodes_total.add_metric(self.default_labels_values + [project], len(nodes))

                    yield project_nodes_total

    def run(self):
        try:
            REGISTRY.register(self)

            logging.info(f"Rundeck exporter server started at {self.args.host}:{self.args.port}...")
            start_http_server(self.args.port, addr=self.args.host, registry=REGISTRY)

            while True:
                sleep(1)
        except OSError as os_error:
            exit_with_msg(msg=str(os_error), level="critical")
