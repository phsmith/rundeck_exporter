#!/usr/bin/env python3
# encoding: utf-8

import re
import logging
import requests
from os import getenv
from time import sleep
from ast import literal_eval
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from cachetools import cached, TTLCache
from prometheus_client import start_http_server
from prometheus_client.core import (
    GaugeMetricFamily,
    CounterMetricFamily,
    InfoMetricFamily,
    REGISTRY
)

# Disable InsecureRequestWarning
requests.urllib3.disable_warnings()


class RundeckMetricsCollector(object):
    default_host = '127.0.0.1'
    default_port = 9620
    rundeck_token = getenv('RUNDECK_TOKEN')

    args_parser = ArgumentParser(description='Rundeck Metrics Exporter')
    args_parser.add_argument('--debug',
                             help='Enable debug mode.',
                             default=getenv('RUNDECK_EXPORTER_DEBUG', False),
                             action='store_true'
                             )
    args_parser.add_argument('--host',
                             help=f'Host binding address. Default: {default_host}.',
                             metavar="RUNDECK_EXPORTER_HOST",
                             default=getenv('RUNDECK_EXPORTER_HOST', default_host)
                             )
    args_parser.add_argument('--port',
                             help=f'Host binding port. Default: {default_port}.',
                             metavar="RUNDECK_EXPORTER_PORT",
                             type=int,
                             default=getenv('RUNDECK_EXPORTER_PORT', default_port)
                             )
    args_parser.add_argument('--rundeck.url',
                             dest='rundeck_url',
                             help='Rundeck Base URL [ REQUIRED ].',
                             default=getenv('RUNDECK_URL')
                             )
    args_parser.add_argument('--rundeck.skip_ssl',
                             dest='rundeck_skip_ssl',
                             help='Rundeck Skip SSL Cert Validate.',
                             default=literal_eval(getenv('RUNDECK_SKIP_SSL', 'False').capitalize()),
                             action='store_true'
                             )
    args_parser.add_argument('--rundeck.api.version',
                             dest='rundeck_api_version',
                             help='Default: 34.',
                             type=int,
                             default=getenv('RUNDECK_API_VERSION', 34)
                             )
    args_parser.add_argument('--rundeck.projects.executions',
                             dest='rundeck_projects_executions',
                             help='Get projects executions metrics.',
                             default=literal_eval(getenv('RUNDECK_PROJECTS_EXECUTIONS', 'False').capitalize()),
                             action='store_true'
                             )
    args_parser.add_argument('--rundeck.projects.filter',
                             dest='rundeck_projects_filter',
                             help='Get executions only from listed projects (delimiter = space).',
                             default=getenv('RUNDECK_PROJECTS_FILTER', []),
                             nargs='+'
                             )
    args_parser.add_argument('--rundeck.projects.executions.cache',
                             dest='rundeck_projects_executions_cache',
                             help='Cache requests for project executions metrics query.',
                             default=literal_eval(getenv('RUNDECK_PROJECTS_EXECUTIONS_CACHE', 'False').capitalize()),
                             action='store_true'
                             )
    args_parser.add_argument('--rundeck.cached.requests.ttl',
                             dest='rundeck_cached_requests_ttl',
                             help='Rundeck cached requests expiration time. Default: 120',
                             type=int,
                             default=getenv('RUNDECK_CACHED_REQUESTS_TTL', 120)
                             )

    args = args_parser.parse_args()

    # Logging configuration
    if args.debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=loglevel)

    def __init__(self):
        if not self.args.rundeck_url or not self.rundeck_token:
            self.exit_with_msg(msg='Rundeck URL and Token are required.', level='critical')

    """
    Method to manage requests on Rundeck API Endpoints
    """
    def request_data_from(self, endpoint: str) -> dict:
        response = None

        try:
            response = requests.get(
                f'{self.args.rundeck_url}/api/{self.args.rundeck_api_version}{endpoint}',
                headers={
                    'Accept': 'application/json',
                    'X-Rundeck-Auth-Token': self.rundeck_token
                },
                verify=not self.args.rundeck_skip_ssl
            )
            response_json = response.json()

            if response_json and isinstance(response.json, dict) and response_json.get('error') is True:
                raise Exception(response_json.get('message'))

            return response_json
        except Exception as error:
            self.exit_with_msg(msg=response.text if response else str(error), level='critical')

    @cached(cache=TTLCache(maxsize=1024, ttl=args.rundeck_cached_requests_ttl))
    def cached_request_data_from(self, endpoint: str) -> dict:
        return self.request_data_from(endpoint)

    """
    Method to get Rundeck projects executions info
    """
    def get_project_executions(self, project: dict):
        counter_name = 'rundeck_project_execution_status'
        project_name = project['name']
        project_executions = None
        project_executions_status = list()
        metrics = None
        endpoint = f'/project/{project_name}/executions?max=1'

        try:
            if self.args.rundeck_projects_executions_cache:
                project_executions = self.cached_request_data_from(endpoint)
            else:
                project_executions = self.request_data_from(endpoint)

            for project_execution in project_executions['executions']:
                if not project_executions:
                    continue

                for status in ['succeeded', 'running', 'failed', 'aborted', 'unknown']:
                    value = 0

                    if project_execution.get('status', 'unknown') == status:
                        value = 1

                    metrics = GaugeMetricFamily(
                        counter_name,
                        f'Rundeck Project {project_name} Execution Status',
                        labels=['project_name', 'job_id', 'job_name', 'status']
                    )

                    metrics.add_metric(
                        [
                            project_execution.get('job', {}).get('id', 'None'),
                            project_execution.get('job', {}).get('name', 'None'),
                            project_name,
                            status
                        ],
                        value
                    )

                    project_executions_status.append(metrics)
        except:
            pass

        return project_executions_status

    """
    Method to get Rundeck system stats
    """
    def get_system_stats(self, system_info: dict):
        for stat, stat_values in system_info['system']['stats'].items():
            if stat in ['cpu', 'memory']:
                continue

            for counter, value in stat_values.items():
                if counter in ['unit', 'duration']:
                    continue
                elif stat == 'uptime' and counter == 'since':
                    value = value['epoch']

                rundeck_system_stats = GaugeMetricFamily(
                    f'rundeck_system_stats_{stat}_{counter}',
                    'Rundeck system stats'
                )

                rundeck_system_stats.add_metric([], value)

                yield rundeck_system_stats

    """
    Method to get Rundeck metrics counters, gauges and timers
    """
    def get_counters(self, metrics: dict):
        for metric, metric_value in metrics.items():
            if not isinstance(metric_value, dict):
                continue

            for counter_name, counter_value in metric_value.items():
                counter_name = re.sub(r'[-.]', '_', counter_name)

                if 'rate' in counter_name.lower():
                    continue

                if not counter_name.startswith('rundeck'):
                    counter_name = 'rundeck_' + counter_name

                if metric == 'counters' and 'status' not in counter_name:
                    counter_value = counter_value['count']
                    rundeck_counters = GaugeMetricFamily(counter_name, 'Rundeck counters metrics')

                    rundeck_counters.add_metric([], counter_value)

                    yield rundeck_counters

                elif metric == 'gauges':
                    counter_value = counter_value['value']

                    if 'services' in counter_name:
                        rundeck_gauges = CounterMetricFamily(counter_name, 'Rundeck gauges metrics')
                    else:
                        rundeck_gauges = GaugeMetricFamily(counter_name, 'Rundeck gauges metrics')

                    if counter_value is not None:
                        rundeck_gauges.add_metric([], counter_value)
                    else:
                        rundeck_gauges.add_metric([], 0)

                    yield rundeck_gauges

                elif metric == 'meters' or metric == 'timers':
                    for counter, value in counter_value.items():
                        if counter == 'count' and not isinstance(value, str):
                            rundeck_meters_timers = CounterMetricFamily(
                                counter_name,
                                f"Rundeck {metric} metrics"
                            )

                            rundeck_meters_timers.add_metric([], value)

                            yield rundeck_meters_timers

    """
    Method to collect Rundeck metrics
    """
    def collect(self):
        metrics = self.request_data_from('/metrics/metrics')
        system_info = self.request_data_from('/system/info')

        """
        Rundeck system info
        """
        rundeck_system_info = InfoMetricFamily('rundeck_system', 'Rundeck system info')
        rundeck_system_info.add_metric([], {x: str(y) for x, y in system_info['system']['rundeck'].items()})
        yield rundeck_system_info

        """
        Rundeck system stats
        """
        for system_stats in self.get_system_stats(system_info):
            yield system_stats

        """
        Rundeck counters
        """
        for counters in self.get_counters(metrics):
            yield counters

        """
        Rundeck projects executions info
        """
        if self.args.rundeck_projects_executions:
            endpoint = '/projects'

            if self.args.rundeck_projects_filter:
                projects = [{"name": x} for x in self.args.rundeck_projects_filter]
            else:
                if self.args.rundeck_projects_executions_cache:
                    projects = self.cached_request_data_from(endpoint)
                else:
                    projects = self.request_data_from(endpoint)

            with ThreadPoolExecutor() as threadpool:
                project_executions = threadpool.map(self.get_project_executions, projects)

                for executions in project_executions:
                    for execution in executions:
                        if execution is not None:
                            yield(execution)

    @staticmethod
    def exit_with_msg(msg: str, level: str):
        getattr(logging, level)(msg)
        exit(getattr(logging, level.upper()))

    @classmethod
    def run(cls):
        try:
            REGISTRY.register(RundeckMetricsCollector())

            logging.info(f'Rundeck exporter server started at {cls.args.host}:{cls.args.port}...')
            start_http_server(cls.args.port, addr=cls.args.host, registry=REGISTRY)

            while True:
                sleep(1)
        except OSError as os_error:
            cls.exit_with_msg(msg=str(os_error), level='critical')


if __name__ == "__main__":
    try:
        RundeckMetricsCollector.run()
    except KeyboardInterrupt:
        logging.info('Rundeck exporter execution finished.')
