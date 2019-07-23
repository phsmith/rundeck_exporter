#!/usr/bin/env python3
# encoding: utf-8

import requests
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
                         default='127.0.0.1'
                         )
args_parser.add_argument('--port',
                         help='Host binding port. Default: 9620',
                         type=int,
                         default=9620
                         )
args_parser.add_argument('--rundeck.token',
                         dest='rundeck_token',
                         help='Rundeck Access Token',
                         required=True
                         )
args_parser.add_argument('--rundeck.url',
                         dest='rundeck_url',
                         help='Rundeck Metrics Url',
                         required=True
                         )
args_parser.add_argument('--rundeck.skip_ssl',
                         dest='rundeck_skip_ssl',
                         help='Rundeck Skip SSL Cert Validate',
                         action='store_false'
                         )
args_parser.add_argument('--rundeck.api.version',
                         dest='rundeck_api_version',
                         help='Default: 31',
                         type=int,
                         default=31
                         )
args = args_parser.parse_args()

# Disable InsecureRequestWarning
requests.urllib3.disable_warnings()


class RundeckMetricsCollector(object):
    @staticmethod
    def rundeck_request_data(rundeck_url, endpoint, token, verify=True):
        response = requests.get(
            '{0}/api/{1}/{2}'.format(rundeck_url, args.rundeck_api_version, endpoint),
            headers={
                'Accept': 'application/json',
                'X-Rundeck-Auth-Token': token
            },
            verify=verify
        )

        try:
            return response.json()
        except Exception as error:
            print('\nError:\n\n{}'.format(response.text))
            return error

    def collect(self):
        get_system_info = self.rundeck_request_data(
            args.rundeck_url,
            'system/info',
            args.rundeck_token,
            args.rundeck_skip_ssl
        )

        get_metrics = self.rundeck_request_data(
            args.rundeck_url,
            'metrics/metrics',
            args.rundeck_token,
            args.rundeck_skip_ssl
        )

        rundeck_system_info = InfoMetricFamily('rundeck_system', 'Rundeck System Info')
        rundeck_system_info.add_metric([], {x: str(y) for x, y in get_system_info['system']['rundeck'].items()})

        yield rundeck_system_info

        for stat, stat_values in get_system_info['system']['stats'].items():
            rundeck_system_stats = GaugeMetricFamily(
                'rundeck_system_stats_' + stat.replace('.', '_'),
                'Rundeck System Stats {}'.format(stat.capitalize()),
                labels=['type']
            )

            for counter, value in stat_values.items():
                if counter != 'unit':
                    if isinstance(value, dict):
                        if stat == 'cpu':
                            value = value['average']
                        elif stat == 'uptime':
                            value = value['epoch']

                    rundeck_system_stats.add_metric([counter], value)

            yield rundeck_system_stats

        rundeck_counters_status = CounterMetricFamily('rundeck_counters_status',
                                                      'Rundeck Counters Metrics',
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
                        rundeck_counters = CounterMetricFamily(counter_name, 'Rundeck Counters Metrics')
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
                                                           'Rundeck Gauges Metrics',
                                                           labels=['type']
                                                           )
                    else:
                        rundeck_gauges = GaugeMetricFamily('_'.join(counter_name), 'Rundeck Gauges Metrics')

                    if counter_value is not None:
                        rundeck_gauges.add_metric([counter_name[-1]], counter_value)
                    else:
                        rundeck_gauges.add_metric([counter_name[-1]], 0)

                    yield rundeck_gauges

                elif metric == 'meters' or metric == 'timers':
                    rundeck_meters_timers = GaugeMetricFamily(
                        counter_name,
                        "Rundeck {} Metrics".format(metric.capitalize()),
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
        except KeyboardInterrupt:
            print('Rundeck exporter execution finished.')


if __name__ == "__main__":
    RundeckMetricsCollector.run()
