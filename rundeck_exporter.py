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
    args_parser.add_argument('--rundeck.token',
                             dest='rundeck_token',
                             help='Rundeck Access Token [ REQUIRED ].',
                             default=getenv('RUNDECK_TOKEN')
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
    args_parser.add_argument('--rundeck.projects.executions.limit',
                             dest='rundeck_projects_executions_limit',
                             help='Limit project executions metrics query. Default: 20',
                             default=getenv('RUNDECK_PROJECTS_EXECUTIONS_LIMIT', 20)
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
        self.client_requests_count = 0
        self.rundeck_node = ''

        if not self.args.rundeck_url or not self.args.rundeck_token:
            self.exit_with_msg('Rundeck URL and Token are required.')

    """
    Method to manage requests on Rundeck API Endpoints
    """
    def request_data_from(self, endpoint: str) -> dict:
        response = requests.get(
                f'{self.args.rundeck_url}/api/{self.args.rundeck_api_version}/{endpoint}',
                headers={
                    'Accept': 'application/json',
                    'X-Rundeck-Auth-Token': self.args.rundeck_token
                },
                verify=not self.args.rundeck_skip_ssl
            )

        try:
            if response:
                self.client_requests_count += 1
            return response.json()
        except requests.exceptions.SSLError:
            self.exit_with_msg('SSL Certificate Verify Failed.')
        except (OSError, requests.exceptions.ConnectionError):
            self.exit_with_msg('Connection error.')
        except Exception as error:
            self.exit_with_msg(response.text if response.text else str(error))

    @cached(cache=TTLCache(maxsize=1024, ttl=args.rundeck_cached_requests_ttl))
    def cached_request_data_from(self, endpoint: str) -> dict:
        return self.request_data_from(endpoint)

    """
    Method to get Rundeck projects executions info
    """
    def get_project_executions(self, project: dict):
        project_name = project['name']
        counter_name = f"rundeck_project_{re.sub(r'[-.]', '_', project_name.lower())}_execution"
        rundeck_project_executions_info = InfoMetricFamily(
            counter_name,
            f'Rundeck Project {project_name} Executions',
            labels=['rundeck_node']
        )

        project_executions = self.cached_request_data_from(
            f"/project/{project_name}/executions?max={self.args.rundeck_projects_executions_limit}"
        )

        for project_execution in project_executions['executions']:
            rundeck_project_executions_info.add_metric(
                [self.rundeck_node],
                {
                    'id': str(project_execution.get('id')),
                    'status': str(project_execution.get('status')),
                    'date_started': str(project_execution.get('date-started', {}).get('unixtime', 0)),
                    'date_ended': str(project_execution.get('date-ended', {}).get('unixtime', 0)),
                    'job_id': str(project_execution.get('job', {}).get('id')),
                    'job_name': str(project_execution.get('job', {}).get('name')),
                    'job_average_duration': str(project_execution.get('job', {}).get('averageDuration', 0))
                }
            )

        return rundeck_project_executions_info

    """
    Method to get Rundeck system stats
    """
    def get_system_stats(self, system_info: dict):
        for stat, stat_values in system_info['system']['stats'].items():
            for counter, value in stat_values.items():
                if counter == 'unit':
                    continue
                elif isinstance(value, dict):
                    if stat == 'cpu':
                        value = value['average']
                    elif stat == 'uptime':
                        value = value['epoch']

                rundeck_system_stats = GaugeMetricFamily(
                    f'rundeck_system_stats_{stat}_{counter}',
                    'Rundeck system stats',
                    labels=['rundeck_node']
                )

                rundeck_system_stats.add_metric([self.rundeck_node], value)

                yield rundeck_system_stats

    """
    Method to get Rundeck metrics counters, gauges and timers
    """
    def get_counters(self, metrics: dict):
        rundeck_counters_status = CounterMetricFamily('rundeck_counters_status',
                                                      'Rundeck counters metrics',
                                                      labels=['rundeck_node', 'status'])

        for metric, metric_value in metrics.items():
            if not isinstance(metric_value, dict):
                continue

            for counter_name, counter_value in metric_value.items():
                counter_name = re.sub(r'[-.]', '_', counter_name)

                if not counter_name.startswith('rundeck'):
                    counter_name = 'rundeck_' + counter_name

                if metric == 'counters':
                    counter_value = counter_value['count']

                    if 'status' not in counter_name:
                        rundeck_counters = CounterMetricFamily(counter_name, 'Rundeck counters metrics', labels=['rundeck_node'])
                        rundeck_counters.add_metric([self.rundeck_node], counter_value)
                        yield rundeck_counters
                    else:
                        counter_name = '_'.join(counter_name.split('_')[3:5])
                        rundeck_counters_status.add_metric([self.rundeck_node, counter_name], counter_value)
                elif metric == 'gauges':
                    counter_name = counter_name.split('_')
                    counter_value = counter_value['value']

                    if 'services' in counter_name:
                        rundeck_gauges = GaugeMetricFamily('_'.join(counter_name[:-1]),
                                                           'Rundeck gauges metrics',
                                                           labels=['rundeck_node', 'type']
                                                           )
                    else:
                        rundeck_gauges = GaugeMetricFamily('_'.join(counter_name), 'Rundeck gauges metrics')

                    if counter_value is not None:
                        rundeck_gauges.add_metric([self.rundeck_node, counter_name[-1]], counter_value)
                    else:
                        rundeck_gauges.add_metric([self.rundeck_node, counter_name[-1]], 0)

                    yield rundeck_gauges

                elif metric == 'meters' or metric == 'timers':
                    rundeck_meters_timers = GaugeMetricFamily(
                        counter_name,
                        f"Rundeck {metric} metrics",
                        labels=['rundeck_node', 'type']
                    )

                    for counter, value in counter_value.items():
                        if not isinstance(value, str):
                            if counter_name == 'rundeck_api_requests_requestTimer' and counter == 'count':
                                value -= self.client_requests_count

                            rundeck_meters_timers.add_metric([self.rundeck_node, counter], value)

                    yield rundeck_meters_timers

        yield rundeck_counters_status

    """
    Method to collect Rundeck metrics
    """
    def collect(self):
        metrics = self.request_data_from('/metrics/metrics')
        system_info = self.request_data_from('/system/info')
        self.rundeck_node = system_info['system']['rundeck']['node']

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
            if self.args.rundeck_projects_filter:
                projects = [{"name": x} for x in self.args.rundeck_projects_filter]
            else:
                projects = self.cached_request_data_from('/projects')

            with ThreadPoolExecutor() as threadpool:
                executions = threadpool.map(self.get_project_executions, projects)

            for execution in executions:
                if execution is not None:
                    yield(execution)

    @staticmethod
    def exit_with_msg(msg: str):
        raise SystemExit(f'\nError:\n  {msg}\n')

    @classmethod
    def run(cls):
        try:
            REGISTRY.register(RundeckMetricsCollector())

            logging.info(f'Rundeck exporter server started at {cls.args.host}:{cls.args.port}...')
            start_http_server(cls.args.port, addr=cls.args.host, registry=REGISTRY)
            while True:
                sleep(1)
        except OSError as os_error:
            cls.exit_with_msg(str(os_error))


if __name__ == "__main__":
    try:
        RundeckMetricsCollector.run()
    except KeyboardInterrupt:
        logging.info('Rundeck exporter execution finished.')
