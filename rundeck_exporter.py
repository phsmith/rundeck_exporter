#!/usr/bin/env python3
# encoding: utf-8

import json
import logging
import re
import requests
import textwrap

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from ast import literal_eval
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from enum import Enum
from os import getenv
from time import sleep

from cachetools import cached, TTLCache
from prometheus_client import start_http_server
from prometheus_client.core import (
    GaugeMetricFamily,
    CounterMetricFamily,
    InfoMetricFamily,
    REGISTRY
)

__author__ = 'Phillipe Smith'
__author_email__ = 'phsmithcc@gmail.com'
__app__ = 'rundeck_exporter'
__version__ = open('VERSION').read()

print(__version__)

# Disable InsecureRequestWarning
requests.urllib3.disable_warnings()


class RundeckProjectExecution(Enum):
    '''Class for mapping Rundeck projects execution attributes'''

    START = 1
    DURATION = 2
    STATUS = 3

class RundeckProjectExecutionRecord(object):
    '''Class for keeping track of Rundeck projects execution info'''

    def __init__(self, tags: list, value: float, execution_type: RundeckProjectExecution):
        self.tags = tags
        self.value = value
        self. execution_type = execution_type


class RundeckMetricsCollector(object):
    '''Class for collect Rundeck metrics info'''

    default_host = '127.0.0.1'
    default_port = 9620
    rundeck_token = getenv('RUNDECK_TOKEN')
    rundeck_userpassword = getenv('RUNDECK_USERPASSWORD')

    args_parser = ArgumentParser(
        description=textwrap.dedent('''
            Rundeck Metrics Exporter

            required environment vars:
                RUNDECK_TOKEN\t Rundeck API Token
                RUNDECK_USERPASSWORD Rundeck User Password (RUNDECK_USERNAME or --rundeck.username are required too)
        '''),
        formatter_class=RawDescriptionHelpFormatter
    )
    args_parser.add_argument('--debug',
                             help='Enable debug mode.',
                             default=getenv('RUNDECK_EXPORTER_DEBUG', False),
                             action='store_true'
                             )
    args_parser.add_argument('-v', '--version',
                             help='Shows rundeck_exporter current release version.',
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
    args_parser.add_argument('--rundeck.username',
                             dest='rundeck_username',
                             help='Rundeck User with access to the system information.',
                             default=getenv('RUNDECK_USERNAME'),
                             required=False
                             )
    args_parser.add_argument('--rundeck.projects.executions',
                             dest='rundeck_projects_executions',
                             help='Get projects executions metrics.',
                             default=literal_eval(getenv('RUNDECK_PROJECTS_EXECUTIONS', 'False').capitalize()),
                             action='store_true'
                             )
    args_parser.add_argument('--rundeck.projects.executions.limit',
                             dest='rundeck_projects_executions_limit',
                             help='Project executions max results per query. Default: 20.',
                             type=int,
                             default=getenv('RUNDECK_PROJECTS_EXECUTIONS_LIMIT', 20)
                             )
    args_parser.add_argument('--rundeck.projects.executions.cache',
                             dest='rundeck_projects_executions_cache',
                             help='Cache requests for project executions metrics query.',
                             default=literal_eval(getenv('RUNDECK_PROJECTS_EXECUTIONS_CACHE', 'False').capitalize()),
                             action='store_true'
                             )
    args_parser.add_argument('--rundeck.projects.filter',
                            dest='rundeck_projects_filter',
                            help='Get executions only from listed projects (delimiter = space).',
                            default=getenv('RUNDECK_PROJECTS_FILTER', []),
                            nargs='+'
                            )
    args_parser.add_argument('--rundeck.cached.requests.ttl',
                             dest='rundeck_cached_requests_ttl',
                             help='Rundeck cached requests expiration time. Default: 120',
                             type=int,
                             default=getenv('RUNDECK_CACHED_REQUESTS_TTL', 120)
                             )
    args_parser.add_argument('--rundeck.cpu.stats',
                             dest='rundeck_cpu_stats',
                             help='Show Rundeck CPU usage stats',
                             action='store_true',
                             default=getenv('RUNDECK_CPU_STATS', False)
                             )
    args_parser.add_argument('--rundeck.memory.stats',
                             dest='rundeck_memory_stats',
                             help='Show Rundeck memory usage stats',
                             action='store_true',
                             default=getenv('RUNDECK_MEMORY_STATS', False)
                             )

    args = args_parser.parse_args()

    # Logging configuration
    if args.debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=loglevel)

    def __init__(self):
        if self.args.version:
            print(f'{__app__} {__version__}')
            exit(0)

        if not self.args.rundeck_url \
            or not (self.rundeck_token or self.args.rundeck_username and self.rundeck_userpassword):
            self.exit_with_msg(msg='Rundeck URL and Token or User/Password are required.', level='critical')

        self.instance_address = re.findall(r'https?://([\w\d:._-]+)', self.args.rundeck_url)[0]
        self.default_labels = ['instance_address']
        self.default_labels_values = [self.instance_address]

    """
    Method to manage requests on Rundeck API Endpoints
    """
    def request_data_from(self, endpoint: str) -> dict:
        response = None
        session = requests.Session()

        try:
            if self.args.rundeck_username and self.rundeck_userpassword:
                session.post(
                    f'{self.args.rundeck_url}/j_security_check',
                    data={"j_username": self.args.rundeck_username, "j_password": self.rundeck_userpassword},
                    verify=not self.args.rundeck_skip_ssl
                )

            if endpoint == '/metrics/metrics' and session.cookies.get_dict().get('JSESSIONID'):
                request_url = f'{self.args.rundeck_url}{endpoint}'
                response = session.get(request_url)
                response_json = json.loads(response.text)
            else:
                request_url = f'{self.args.rundeck_url}/api/{self.args.rundeck_api_version}{endpoint}'
                response = session.get(
                    request_url,
                    headers={
                        'Accept': 'application/json',
                        'X-Rundeck-Auth-Token': self.rundeck_token
                    },
                    verify=not self.args.rundeck_skip_ssl
                )
                response_json = response.json()

            if response_json and isinstance(response_json, dict) and response_json.get('error') is True:
                raise Exception(response_json.get('message'))

            return response_json
        except json.JSONDecodeError as error:
            self.exit_with_msg(msg=f'Invalid JSON Response from {request_url}', level='critical')
        except Exception as error:
            self.exit_with_msg(msg=response.text if response else str(error), level='critical')

    @cached(cache=TTLCache(maxsize=1024, ttl=args.rundeck_cached_requests_ttl))
    def cached_request_data_from(self, endpoint: str) -> dict:
        return self.request_data_from(endpoint)

    """
    Method to get Rundeck projects executions info
    """
    def get_project_executions(self, project: dict):
        project_name = project['name']
        project_execution_records = list()
        project_executions_limit = self.args.rundeck_projects_executions_limit
        endpoint = f'/project/{project_name}/executions?recentFilter=1d&max={project_executions_limit}'
        endpoint_running_executions = f'/project/{project_name}/executions/running?recentFilter=1d&max={project_executions_limit}'

        try:
            if self.args.rundeck_projects_executions_cache:
                project_executions_running_info = self.cached_request_data_from(endpoint_running_executions)
                project_executions_info = self.cached_request_data_from(endpoint)
            else:
                project_executions_running_info = self.request_data_from(endpoint_running_executions)
                project_executions_info = self.request_data_from(endpoint)

            project_executions_total = {
                'project': project_name,
                'total_executions': project_executions_info['paging']['total']
            }
            project_executions = (project_executions_running_info.get('executions', [])
                                  + project_executions_info.get('executions', []))

            for project_execution in project_executions:
                job_info = project_execution.get('job', {})
                job_id = job_info.get('id', 'None')
                job_name = job_info.get('name', 'None')
                job_group = job_info.get('group', 'None')
                execution_id = str(project_execution.get('id', 'None'))
                execution_type = project_execution.get('executionType')
                user = project_execution.get('user')
                default_metrics = self.default_labels_values + [
                    project_name,
                    job_id,
                    job_name,
                    job_group,
                    execution_id,
                    execution_type,
                    user
                ]

                # Job start/end times
                timestamp_now = datetime.now().timestamp() * 1000
                job_start_time = project_execution.get('date-started', {}).get('unixtime', 0)
                job_end_time = project_execution.get('date-ended', {}).get('unixtime', timestamp_now)
                job_execution_duration = (job_end_time - job_start_time) / 1000

                project_execution_records.append(
                    RundeckProjectExecutionRecord(default_metrics, job_start_time, RundeckProjectExecution.START)
                )
                project_execution_records.append(
                    RundeckProjectExecutionRecord(default_metrics, job_execution_duration, RundeckProjectExecution.DURATION)
                )

                for status in ['succeeded', 'running', 'failed', 'aborted', 'unknown']:
                    value = 0

                    if project_execution.get('status', 'unknown') == status:
                        value = 1

                    project_execution_records.append(
                        RundeckProjectExecutionRecord(default_metrics + [status], value, RundeckProjectExecution.STATUS)
                    )

        except Exception as error:  # nosec
            logging.error(error)

        return project_execution_records, project_executions_total


    """
    Method to get Rundeck system stats
    """
    def get_system_stats(self, system_info: dict):
        for stat, stat_values in system_info['system']['stats'].items():
            for counter, value in stat_values.items():
                if counter in ['unit', 'duration']:
                    continue
                elif stat == 'uptime' and counter == 'since':
                    value = value['epoch']
                elif stat == 'cpu':
                    if self.args.rundeck_cpu_stats and isinstance(value, dict):
                        counter = f'{counter}_ratio'
                        value = value['average']
                    else:
                        continue
                elif stat == 'memory':
                    if self.args.rundeck_memory_stats:
                        counter = f'{counter}_bytes'
                    else:
                        continue

                rundeck_system_stats = GaugeMetricFamily(
                    name=f'rundeck_system_stats_{stat}_{counter}',
                    documentation='Rundeck system stats',
                    labels=self.default_labels
                )

                rundeck_system_stats.add_metric(self.default_labels_values, value)

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

                rundeck_meters_timers = CounterMetricFamily(
                    name=counter_name,
                    documentation=f"Rundeck {metric} metrics",
                    labels=self.default_labels
                )
                rundeck_counters = GaugeMetricFamily(
                    name=counter_name,
                    documentation='Rundeck counters metrics',
                    labels=self.default_labels
                )
                rundeck_gauges = GaugeMetricFamily(
                    name=counter_name,
                    documentation='Rundeck gauges metrics',
                    labels=self.default_labels
                )

                if 'rate' in counter_name.lower():
                    continue

                if not counter_name.startswith('rundeck'):
                    counter_name = 'rundeck_' + counter_name

                if metric == 'counters' and 'status' not in counter_name:
                    counter_value = counter_value['count']
                    rundeck_counters.add_metric(self.default_labels_values, counter_value)

                    yield rundeck_counters

                elif metric == 'gauges':
                    counter_value = counter_value['value']

                    if 'services' in counter_name:
                        services_trackers = rundeck_gauges
                    else:
                        services_trackers = rundeck_counters

                    if counter_value is not None:
                        services_trackers.add_metric(self.default_labels_values, counter_value)
                    else:
                        services_trackers.add_metric(self.default_labels_values, 0)

                    yield services_trackers

                elif metric == 'meters' or metric == 'timers':
                    for counter, value in counter_value.items():
                        if counter == 'count' and not isinstance(value, str):

                            rundeck_meters_timers.add_metric(self.default_labels_values, value)

                            yield rundeck_meters_timers

    """
    Method to collect Rundeck metrics
    """
    def collect(self):
        """
        Rundeck system info
        """
        system_info = self.request_data_from('/system/info')
        api_version = int(system_info['system']['rundeck']['apiversion'])
        rundeck_system_info = InfoMetricFamily(
            name='rundeck_system',
            documentation='Rundeck system info',
            labels=self.default_labels
        )
        rundeck_system_info.add_metric(self.default_labels_values, {x: str(y) for x, y in system_info['system']['rundeck'].items()})
        yield rundeck_system_info

        """
        Rundeck system stats
        """
        for system_stats in self.get_system_stats(system_info):
            yield system_stats

        """
        Rundeck counters
        """
        if api_version >= self.args.rundeck_api_version < 25 \
            and not (self.args.rundeck_username and self.rundeck_userpassword):
            logging.warning(f'Unsupported API version "{self.args.rundeck_api_version}"'
                            + f' for API request: /api/{self.args.rundeck_api_version}/metrics/metrics.'
                            + ' Minimum supported version is 25.'
                            + ' Some metrics like rundeck_scheduler_quartz_* will not be available.'
                            + ' Use Username and Password options to get the metrics.')
        else:
            metrics = self.request_data_from('/metrics/metrics')

            for counters in self.get_counters(metrics):
                yield counters

        """
        Rundeck projects executions info
        """
        rundeck_projects_filter = self.args.rundeck_projects_filter

        if self.args.rundeck_projects_executions:
            endpoint = '/projects'

            if rundeck_projects_filter:
                if isinstance(rundeck_projects_filter, str):
                    rundeck_projects_filter = rundeck_projects_filter.split()

                projects = [{"name": x} for x in rundeck_projects_filter]
            else:
                if self.args.rundeck_projects_executions_cache:
                    projects = self.cached_request_data_from(endpoint)
                else:
                    projects = self.request_data_from(endpoint)

            with ThreadPoolExecutor() as threadpool:
                project_execution_records = threadpool.map(self.get_project_executions, projects)

                default_labels = self.default_labels + [
                    'project_name',
                    'job_id',
                    'job_name',
                    'job_group',
                    'execution_id',
                    'execution_type',
                    'user'
                ]

                project_start_metrics = GaugeMetricFamily(
                    'rundeck_project_start_timestamp',
                    f'Rundeck Project ProjectName Start Timestamp',
                    labels=default_labels
                )

                project_duration_metrics = GaugeMetricFamily(
                    'rundeck_project_execution_duration_seconds',
                    f'Rundeck Project ProjectName Execution Duration',
                    labels=default_labels
                )

                project_metrics = GaugeMetricFamily(
                    'rundeck_project_execution_status',
                    f'Rundeck Project ProjectName Execution Status',
                    labels=default_labels + ['status']
                )

                project_executions_total_metrics = CounterMetricFamily(
                    'rundeck_project_executions_total',
                    f'Rundeck Project ProjectName Total Executions',
                    labels=self.default_labels + ['project_name']
                )

                for project_execution_record_group, project_executions_total in project_execution_records:
                    project_executions_total_metrics.add_metric(
                        self.default_labels_values + [project_executions_total['project']],
                        project_executions_total['total_executions']
                    )
                    for project_execution_record in project_execution_record_group:
                        if project_execution_record.execution_type == RundeckProjectExecution.START:
                            project_start_metrics.add_metric(project_execution_record.tags, project_execution_record.value)
                        elif project_execution_record.execution_type == RundeckProjectExecution.DURATION:
                            project_duration_metrics.add_metric(project_execution_record.tags, project_execution_record.value)
                        elif project_execution_record.execution_type == RundeckProjectExecution.STATUS:
                            project_metrics.add_metric(project_execution_record.tags, project_execution_record.value)

                yield project_start_metrics
                yield project_duration_metrics
                yield project_metrics
                yield project_executions_total_metrics

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
