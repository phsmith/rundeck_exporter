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
  --host HOST           Host binding address. Default: 127.0.0.1
  --port PORT           Host binding port. Default: 9620
  --rundeck.token RUNDECK_TOKEN
                        Rundeck Access Token
  --rundeck.url RUNDECK_URL
                        Rundeck Metrics Url
  --rundeck.skip_ssl    Rundeck Skip SSL Cert Validate
  --rundeck.api.version RUNDECK_API_VERSION
                        Default: 31
```

Example output:


```
$ curl -s http://127.0.0.1:9620

...
# HELP rundeck_system_info Rundeck System Info
# TYPE rundeck_system_info gauge
rundeck_system_info{apiversion="31",base="/home/rundeck",build="3.0.21-20190424",buildGit="v3.0.21-0-g3ee1526",node="desenv-sgh-rundeck-6bd9669757-g5kkt",serverUUID="fbfc30f3-5b70-4fe7-899f-c818fc75d439",version="3.0.21-20190424"} 1.0
# HELP rundeck_system_stats_uptime Rundeck System Stats Uptime
# TYPE rundeck_system_stats_uptime gauge
rundeck_system_stats_uptime{type="duration"} 5.78574872e+08
rundeck_system_stats_uptime{type="since"} 1.563302987471e+012
# HELP rundeck_system_stats_cpu Rundeck System Stats Cpu
# TYPE rundeck_system_stats_cpu gauge
rundeck_system_stats_cpu{type="loadAverage"} 7.68115234375
rundeck_system_stats_cpu{type="processors"} 3.0
# HELP rundeck_system_stats_memory Rundeck System Stats Memory
# TYPE rundeck_system_stats_memory gauge
rundeck_system_stats_memory{type="max"} 1.908932608e+09
rundeck_system_stats_memory{type="free"} 6.6446712e+08
rundeck_system_stats_memory{type="total"} 1.112014848e+09
# HELP rundeck_system_stats_scheduler Rundeck System Stats Scheduler
# TYPE rundeck_system_stats_scheduler gauge
rundeck_system_stats_scheduler{type="running"} 0.0
rundeck_system_stats_scheduler{type="threadPoolSize"} 10.0
# HELP rundeck_system_stats_threads Rundeck System Stats Threads
# TYPE rundeck_system_stats_threads gauge
rundeck_system_stats_threads{type="active"} 33.0
# HELP rundeck_dataSource_connection_pingTime Rundeck Gauges Metrics
# TYPE rundeck_dataSource_connection_pingTime gauge
rundeck_dataSource_connection_pingTime 0.0
# HELP rundeck_gauge_response_static_star_star Rundeck Gauges Metrics
# TYPE rundeck_gauge_response_static_star_star gauge
rundeck_gauge_response_static_star_star 7.0
# HELP rundeck_gauge_response_unmapped Rundeck Gauges Metrics
# TYPE rundeck_gauge_response_unmapped gauge
rundeck_gauge_response_unmapped 84.0
# HELP rundeck_scheduler_quartz_runningExecutions Rundeck Gauges Metrics
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
