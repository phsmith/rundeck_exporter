#!/usr/bin/env python3
# encoding: utf-8

import requests
from os import getenv
from time import sleep
from argparse import ArgumentParser
from prometheus_client import start_http_server
from prometheus_client.core import (
    GaugeMetricFamily,
    CounterMetricFamily,
    InfoMetricFamily,
    REGISTRY
)

args_parser = ArgumentParser(description='Rundeck Metrics Exporter')
args_parser.add_argument('--host',
                         help='Host binding address. Default: 127.0.0.1',
                         metavar="RUNDECK_EXPORTER_HOST",
                         default=getenv('RUNDECK_EXPORTER_HOST', '127.0.0.1')
                         )
args_parser.add_argument('--port',
                         help='Host binding port. Default: 9620',
                         metavar="RUNDECK_EXPORTER_PORT",
                         type=int,
                         default=getenv('RUNDECK_EXPORTER_PORT', 9620)
                         )
args_parser.add_argument('--rundeck.token',
                         dest='rundeck_token',
                         help='Rundeck Access Token [ REQUIRED ]',
                         default=getenv('RUNDECK_TOKEN')
                         )
args_parser.add_argument('--rundeck.url',
                         dest='rundeck_url',
                         help='Rundeck Base URL [ REQUIRED ]',
                         default=getenv('RUNDECK_URL')
                         )
args_parser.add_argument('--rundeck.skip_ssl',
                         dest='rundeck_skip_ssl',
                         help='Rundeck Skip SSL Cert Validate',
                         default=getenv('RUNDECK_SKIP_SSL'),
                         action='store_true'
                         )
args_parser.add_argument('--rundeck.api.version',
                         dest='rundeck_api_version',
                         help='Default: 31',
                         type=int,
                         default=getenv('RUNDECK_API_VERSION', 31)
                         )

args = args_parser.parse_args()

if not args.rundeck_url and not args.rundeck_token:
    args_parser.print_help()
    exit(1)

# Disable InsecureRequestWarning
requests.urllib3.disable_warnings()


class RundeckMetricsCollector(object):
    @staticmethod
    def rundeck_request_data(rundeck_url, endpoint, token, verify=True):
        try:
            response = requests.get(
                '{0}/api/{1}/{2}'.format(rundeck_url, args.rundeck_api_version, endpoint),
                headers={
                    'Accept': 'application/json',
                    'X-Rundeck-Auth-Token': token
                },
                verify=verify
            )

            return response.json()
        except requests.exceptions.SSLError:
            print('\nError:\n  SSL Certificate Verify Failed.\n')
            exit(1)
        except Exception as error:
            print('\nError:\n\n{}'.format(response.text))
            return error

    def collect(self):
        ssl_verify = False if str(args.rundeck_skip_ssl) in ['1', 'yes', 'True'] else True

        get_system_info = self.rundeck_request_data(
            args.rundeck_url,
            'system/info',
            args.rundeck_token,
            ssl_verify
        )

        get_metrics = self.rundeck_request_data(
            args.rundeck_url,
            'metrics/metrics',
            args.rundeck_token,
            ssl_verify
        )

        rundeck_system_info = InfoMetricFamily('rundeck_system', 'Rundeck system info')
        rundeck_system_info.add_metric([], {x: str(y) for x, y in get_system_info['system']['rundeck'].items()})

        yield rundeck_system_info

        for stat, stat_values in get_system_info['system']['stats'].items():
            for counter, value in stat_values.items():
                if counter == 'unit':
                    continue
                elif isinstance(value, dict):
                    if stat == 'cpu':
                        value = value['average']
                    elif stat == 'uptime':
                        value = value['epoch']

                rundeck_system_stats = GaugeMetricFamily(
                    'rundeck_system_stats_{}_{}'.format(stat, counter),
                    'Rundeck system stats'
                )

                rundeck_system_stats.add_metric([], value)

                yield rundeck_system_stats

        rundeck_counters_status = CounterMetricFamily('rundeck_counters_status',
                                                      'Rundeck counters metrics',
                                                      labels=['status'])

        for metric, metric_value in get_metrics.items():
            if not isinstance(metric_value, dict):
                continue

            for counter_name, counter_value in metric_value.items():
                counter_name = counter_name.replace('.', '_').replace('-', '_')

                if not counter_name.startswith('rundeck'):
                    counter_name = 'rundeck_' + counter_name

                if metric == 'counters':
                    counter_value = counter_value['count']

                    if 'status' not in counter_name:
                        rundeck_counters = CounterMetricFamily(counter_name, 'Rundeck counters metrics')
                        rundeck_counters.add_metric([], counter_value)
                        yield rundeck_counters
                    else:
                        counter_name = '_'.join(counter_name.split('_')[3:5])
                        rundeck_counters_status.add_metric([counter_name], counter_value)

                elif metric == 'gauges':
                    counter_name = counter_name.split('_')
                    counter_value = counter_value['value']

                    if 'services' in counter_name:
                        rundeck_gauges = GaugeMetricFamily('_'.join(counter_name[:-1]),
                                                           'Rundeck gauges metrics',
                                                           labels=['type']
                                                           )
                    else:
                        rundeck_gauges = GaugeMetricFamily('_'.join(counter_name), 'Rundeck gauges metrics')

                    if counter_value is not None:
                        rundeck_gauges.add_metric([counter_name[-1]], counter_value)
                    else:
                        rundeck_gauges.add_metric([counter_name[-1]], 0)

                    yield rundeck_gauges

                elif metric == 'meters' or metric == 'timers':
                    rundeck_meters_timers = GaugeMetricFamily(
                        counter_name,
                        "Rundeck {} metrics".format(metric),
                        labels=['type']
                    )

                    for counter, value in counter_value.items():
                        if not isinstance(value, str):
                            rundeck_meters_timers.add_metric([counter], value)

                    yield rundeck_meters_timers

        yield rundeck_counters_status

    @staticmethod
    def run():
        try:
            start_http_server(args.port, addr=args.host)
            print('Rundeck exporter server started at {}:{}...'.format(args.host, args.port))

            REGISTRY.register(RundeckMetricsCollector())

            while True:
                sleep(1)
        except OSError as os_error:
            print('\nError:\n {}'.format(os_error))
        except KeyboardInterrupt:
            print('Rundeck exporter execution finished.')


if __name__ == "__main__":
    RundeckMetricsCollector.run()
