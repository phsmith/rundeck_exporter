## Rundeck_Exporter

Rundeck Metrics Exporter for Prometheus.

This exporter uses the prometheus_client and requests Python module to expose Rundeck metrics found in:

 * RUNDECK_URL/api/*version*/system/info
 * RUNDECK_URL/api/*version*/metrics/metrics

 Where *version* represents the Rundeck API version, like: 29,30,31,etc.

 This code was tested on Rundeck API version 31.

## Metrics

All metrics are exported with **rundeck_** prefix.

## Dependencies

* A Rundeck token with permissions to make API requests
* The following python modules:
```
pip install prometheus-client requests
```

## Usage

The rundeck_exporter supports the following paramenters:

```
$ ./rundeck_exporter.py -h

Rundeck Metrics Exporter

optional arguments:
  -h, --help            show this help message and exit
  --host RUNDECK_EXPORTER_HOST
                        Host binding address. Default: 127.0.0.1
  --port RUNDECK_EXPORTER_PORT
                        Host binding port. Default: 9620
  --rundeck.token RUNDECK_TOKEN
                        Rundeck Access Token [ REQUIRED ]
  --rundeck.url RUNDECK_URL
                        Rundeck Base URL [ REQUIRED ]
  --rundeck.skip_ssl    Rundeck Skip SSL Cert Validate
  --rundeck.api.version RUNDECK_API_VERSION
                        Default: 31
```

Optionally, it's possible to pass the following environment variables to the rundeck_exporter:

| Variable | Description |
| ------ | ------ |
| RUNDECK_EXPORTER_HOST | Binding address. Default: 127.0.0.1 |
| RUNDECK_EXPORTER_PORT | Binding port. Default: 9620 |
| RUNDECK_URL (required) | Rundeck base URL |
| RUNDECK_TOKEN (required) | Rundeck access token |
| RUNDECK_API_VERSION | Rundeck API version. Default: 31 |
| RUNDECK_SKIP_SSL | Skip SSL certificate check. Default: False |


Example output:


```
$ curl -s http://127.0.0.1:9620

...
# HELP rundeck_system_info Rundeck system info
# TYPE rundeck_system_info gauge
rundeck_system_info{apiversion="31",base="/home/rundeck",build="3.0.21-20190424",buildGit="v3.0.21-0-g3ee1526",node="desenv-sgh-rundeck-6bd9669757-g5kkt",serverUUID="fbfc30f3-5b70-4fe7-899f-c818fc75d439",version="3.0.21-20190424"} 1.0
# HELP rundeck_system_stats_uptime_duration Rundeck system stats
# TYPE rundeck_system_stats_uptime_duration gauge
rundeck_system_stats_uptime_duration 1.288533174e+09
# HELP rundeck_system_stats_uptime_since Rundeck system stats
# TYPE rundeck_system_stats_uptime_since gauge
rundeck_system_stats_uptime_since 1.563303020049e+012
# HELP rundeck_system_stats_cpu_loadAverage Rundeck system stats
# TYPE rundeck_system_stats_cpu_loadAverage gauge
rundeck_system_stats_cpu_loadAverage 5.52099609375
# HELP rundeck_system_stats_cpu_processors Rundeck system stats
# TYPE rundeck_system_stats_cpu_processors gauge
rundeck_system_stats_cpu_processors 3.0
# HELP rundeck_system_stats_memory_max Rundeck system stats
# TYPE rundeck_system_stats_memory_max gauge
rundeck_system_stats_memory_max 1.908932608e+09
# HELP rundeck_system_stats_memory_free Rundeck system stats
# TYPE rundeck_system_stats_memory_free gauge
rundeck_system_stats_memory_free 6.1858224e+07
# HELP rundeck_system_stats_memory_total Rundeck system stats
# TYPE rundeck_system_stats_memory_total gauge
rundeck_system_stats_memory_total 3.41835776e+08
# HELP rundeck_system_stats_scheduler_running Rundeck system stats
# TYPE rundeck_system_stats_scheduler_running gauge
rundeck_system_stats_scheduler_running 0.0
# HELP rundeck_system_stats_scheduler_threadPoolSize Rundeck system stats
# TYPE rundeck_system_stats_scheduler_threadPoolSize gauge
rundeck_system_stats_scheduler_threadPoolSize 10.0
# HELP rundeck_system_stats_threads_active Rundeck system stats
# TYPE rundeck_system_stats_threads_active gauge
rundeck_system_stats_threads_active 37.0
# HELP rundeck_dataSource_connection_pingTime Rundeck gauges metrics
# TYPE rundeck_dataSource_connection_pingTime gauge
rundeck_dataSource_connection_pingTime 0.0
# HELP rundeck_gauge_response_static_star_star Rundeck gauges metrics
# TYPE rundeck_gauge_response_static_star_star gauge
rundeck_gauge_response_static_star_star 11.0
# HELP rundeck_gauge_response_unmapped Rundeck gauges metrics
# TYPE rundeck_gauge_response_unmapped gauge
rundeck_gauge_response_unmapped 58.0
# HELP rundeck_scheduler_quartz_runningExecutions Rundeck gauges metrics
# TYPE rundeck_scheduler_quartz_runningExecutions gauge
rundeck_scheduler_quartz_runningExecutions 0.0
....
```

#### Running in Docker

```
docker build -t rundeck_exporter .

docker run --rm -d -p 9620:9620 rundeck_exporter \
--host 0.0.0.0 \
--rundeck.url https://rundeck.test.com \
--rundeck.token abcdef0123456789 \
--rundeck.skip_ssl
```

## Changelog

`v1.0.0`:
* Initial release

`v1.1.0`:
* Support for environment variables
* Better excpetions treatment

`v1.1.1`:
* Fixed metrics collection bug

