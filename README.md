## Rundeck_Exporter

[![Docker Pulls](https://img.shields.io/docker/pulls/phsmith/rundeck-exporter?logo=docker&)](https://hub.docker.com/r/phsmith/rundeck-exporter)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/phsmith/rundeck_exporter?color=%23e3e3e3)](https://github.com/phsmith/rundeck_exporter/releases)

Rundeck Metrics Exporter for Prometheus.

![Rundeck-Grafana-Dashboard](examples/grafana/rundeck-grafana-dashboard.png)

*Dashboard example can be found in: [examples/grafana](examples/grafana)*

This exporter uses the prometheus_client and requests Python module to expose Rundeck metrics found in:

 * RUNDECK_URL/*api_version*/system/info
 * RUNDECK_URL/*api_version*/metrics/metrics

 Where *version* represents the Rundeck API version, like: 31,32,33,34,etc.

 This code was tested on Rundeck API version 31+.

 > **Warning**:
 > Since version 4.x.x. the `/api/V/metrics` endpoint is disabled, so you need to enable it in `rundeck-config.properties` to get the exporter to work. See [config-file-reference.html#metrics-capturing](https://docs.rundeck.com/docs/administration/configuration/config-file-reference.html#metrics-capturing)

## Metrics

All metrics are exported with **rundeck_** prefix.

More detailed information about the metrics can be found in [Documentations](docs/README.md)

## Dependencies

* A Rundeck token with permissions to make API requests
* The following python modules:
```
pip install prometheus-client requests cachetools
```

## Usage

Rundeck token or username and password are required.

The token (`RUNDECK_TOKEN`) or password (`RUNDECK_USERPASSWORD`) must be passed as environment variables to work.

The rundeck_exporter supports the following paramenters:

```
$ ./rundeck_exporter.py --help

usage: rundeck_exporter.py [-h] [--debug] [-v] [--host RUNDECK_EXPORTER_HOST] [--port RUNDECK_EXPORTER_PORT] [--rundeck.url RUNDECK_URL] [--rundeck.skip_ssl]
                           [--rundeck.api.version RUNDECK_API_VERSION] [--rundeck.username RUNDECK_USERNAME] [--rundeck.projects.executions]
                           [--rundeck.projects.executions.limit RUNDECK_PROJECTS_EXECUTIONS_LIMIT] [--rundeck.projects.executions.cache]
                           [--rundeck.projects.filter RUNDECK_PROJECTS_FILTER [RUNDECK_PROJECTS_FILTER ...]] [--rundeck.cached.requests.ttl RUNDECK_CACHED_REQUESTS_TTL]
                           [--rundeck.cpu.stats] [--rundeck.memory.stats]

Rundeck Metrics Exporter

required environment vars:
    RUNDECK_TOKEN        Rundeck API Token
    RUNDECK_USERPASSWORD Rundeck User Password (RUNDECK_USERNAME or --rundeck.username are required too)

options:
  -h, --help            show this help message and exit
  --debug               Enable debug mode.
  -v, --version         Shows rundeck_exporter current release version.
  --host RUNDECK_EXPORTER_HOST
                        Host binding address. Default: 127.0.0.1.
  --port RUNDECK_EXPORTER_PORT
                        Host binding port. Default: 9620.
  --rundeck.url RUNDECK_URL
                        Rundeck Base URL [ REQUIRED ].
  --rundeck.skip_ssl    Rundeck Skip SSL Cert Validate.
  --rundeck.api.version RUNDECK_API_VERSION
                        Default: 34.
  --rundeck.username RUNDECK_USERNAME
                        Rundeck User with access to the system information.
  --rundeck.projects.executions
                        Get projects executions metrics.
  --rundeck.projects.executions.limit RUNDECK_PROJECTS_EXECUTIONS_LIMIT
                        Project executions max results per query. Default: 20.
  --rundeck.projects.executions.cache
                        Cache requests for project executions metrics query.
  --rundeck.projects.filter RUNDECK_PROJECTS_FILTER [RUNDECK_PROJECTS_FILTER ...]
                        Get executions only from listed projects (delimiter = space).
  --rundeck.cached.requests.ttl RUNDECK_CACHED_REQUESTS_TTL
                        Rundeck cached requests expiration time. Default: 120
  --rundeck.cpu.stats   Show Rundeck CPU usage stats
  --rundeck.memory.stats
                        Show Rundeck memory usage stats
```

Optionally, it's possible to pass the following environment variables to the rundeck_exporter:

| Variable | Options |  Description |
| ------ | ------ | ------ |
| RUNDECK_EXPORTER_DEBUG | <ul><li>True</li><li>False (default)</li></ul> | Enable debug mode |
| RUNDECK_EXPORTER_HOST | Default: 127.0.0.1 | Binding address. |
| RUNDECK_EXPORTER_PORT | Default: 9620 | Binding port. |
| RUNDECK_URL (required) | | Rundeck base URL |
| RUNDECK_TOKEN (required) | | Rundeck access token |
| RUNDECK_USERNAME | | Rundeck User with access to the system information |
| RUNDECK_USERPASSWORD | | Rundeck User Password (RUNDECK_USERNAME or --rundeck.username are required too) |
| RUNDECK_API_VERSION | Default: 31 | Rundeck API version. |
| RUNDECK_SKIP_SSL | <ul><li>True</li><li>False (default)</li></ul> | Skip SSL certificate check. |
| RUNDECK_PROJECTS_EXECUTIONS | <ul><li>True</li><li>False (default)</li></ul> | Get projects executions metrics. |
| RUNDECK_PROJECTS_FILTER | | Get executions only from listed projects e.g. "project-1 project-2 ..." |
| RUNDECK_PROJECTS_EXECUTIONS_LIMIT | Default: 20 | Projects executions max results per query |
| RUNDECK_PROJECTS_EXECUTIONS_CACHE | <ul><li>True</li><li>False (default)</li></ul> | Cache requests for project executions metrics query. |
| RUNDECK_CACHED_REQUESTS_TTL | Default: 120 | Rundeck cached requests expiration time. |
| RUNDECK_CPU_STATS | <ul><li>True</li><li>False (default)</li></ul> | Show Rundeck CPU usage stats |
| RUNDECK_MEMORY_STATS | <ul><li>True</li><li>False (default)</li></ul> | Show Rundeck memory usage stats |

<details>
  <summary>
    Output example:
  </summary>

  ```
  $ curl -s http://127.0.0.1:9620

  # TYPE python_gc_objects_collected_total counter
  python_gc_objects_collected_total{generation="0"} 1030.0
  python_gc_objects_collected_total{generation="1"} 170.0
  python_gc_objects_collected_total{generation="2"} 0.0
  # HELP python_gc_objects_uncollectable_total Uncollectable object found during GC
  # TYPE python_gc_objects_uncollectable_total counter
  python_gc_objects_uncollectable_total{generation="0"} 0.0
  python_gc_objects_uncollectable_total{generation="1"} 0.0
  python_gc_objects_uncollectable_total{generation="2"} 0.0
  # HELP python_gc_collections_total Number of times this generation was collected
  # TYPE python_gc_collections_total counter
  python_gc_collections_total{generation="0"} 108.0
  python_gc_collections_total{generation="1"} 9.0
  python_gc_collections_total{generation="2"} 0.0
  # HELP python_info Python platform information
  # TYPE python_info gauge
  python_info{implementation="CPython",major="3",minor="10",patchlevel="2",version="3.10.2"} 1.0
  # HELP process_virtual_memory_bytes Virtual memory size in bytes.
  # TYPE process_virtual_memory_bytes gauge
  process_virtual_memory_bytes 6.54348288e+08
  # HELP process_resident_memory_bytes Resident memory size in bytes.
  # TYPE process_resident_memory_bytes gauge
  process_resident_memory_bytes 3.9170048e+07
  # HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
  # TYPE process_start_time_seconds gauge
  process_start_time_seconds 1.64648236585e+09
  # HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
  # TYPE process_cpu_seconds_total counter
  process_cpu_seconds_total 0.61
  # HELP process_open_fds Number of open file descriptors.
  # TYPE process_open_fds gauge
  process_open_fds 7.0
  # HELP process_max_fds Maximum number of open file descriptors.
  # TYPE process_max_fds gauge
  process_max_fds 8192.0
  # HELP rundeck_system_info Rundeck system info
  # TYPE rundeck_system_info gauge
  rundeck_system_info{apiversion="40",base="/home/rundeck",build="3.4.8-20211214",buildGit="v3.4.8-0-g62288dc",instance_address="localhost:4440",node="e95f20a5cf9b",serverUUID="a14bc3e6-75e8-4fe4-a90d-a16dcc976bf6",version="3.4.8-20211214"} 1.0
  # HELP rundeck_system_stats_uptime_since Rundeck system stats
  # TYPE rundeck_system_stats_uptime_since gauge
  rundeck_system_stats_uptime_since{instance_address="localhost:4440"} 1.64648126618e+012
  # HELP rundeck_system_stats_scheduler_running Rundeck system stats
  # TYPE rundeck_system_stats_scheduler_running gauge
  rundeck_system_stats_scheduler_running{instance_address="localhost:4440"} 0.0
  # HELP rundeck_system_stats_scheduler_threadPoolSize Rundeck system stats
  # TYPE rundeck_system_stats_scheduler_threadPoolSize gauge
  rundeck_system_stats_scheduler_threadPoolSize{instance_address="localhost:4440"} 10.0
  # HELP rundeck_system_stats_threads_active Rundeck system stats
  # TYPE rundeck_system_stats_threads_active gauge
  rundeck_system_stats_threads_active{instance_address="localhost:4440"} 39.0
  # HELP rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_evictionCount Rundeck gauges metrics
  # TYPE rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_evictionCount gauge
  rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_evictionCount{instance_address="localhost:4440"} 0.0
  # HELP rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_hitCount Rundeck gauges metrics
  # TYPE rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_hitCount gauge
  rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_hitCount{instance_address="localhost:4440"} 0.0
  # HELP rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_loadExceptionCount Rundeck gauges metrics
  # TYPE rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_loadExceptionCount gauge
  rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_loadExceptionCount{instance_address="localhost:4440"} 0.0
  # HELP rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_missCount Rundeck gauges metrics
  # TYPE rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_missCount gauge
  rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_missCount{instance_address="localhost:4440"} 0.0
  # HELP rundeck_dataSource_connection_pingTime Rundeck gauges metrics
  # TYPE rundeck_dataSource_connection_pingTime gauge
  rundeck_dataSource_connection_pingTime{instance_address="localhost:4440"} 0.0
  # HELP rundeck_scheduler_quartz_runningExecutions Rundeck gauges metrics
  # TYPE rundeck_scheduler_quartz_runningExecutions gauge
  rundeck_scheduler_quartz_runningExecutions{instance_address="localhost:4440"} 0.0
  # HELP rundeck_services_AuthorizationService_sourceCache_evictionCount_total Rundeck gauges metrics
  # TYPE rundeck_services_AuthorizationService_sourceCache_evictionCount_total counter
  rundeck_services_AuthorizationService_sourceCache_evictionCount_total{instance_address="localhost:4440"} 0.0
  # HELP rundeck_services_AuthorizationService_sourceCache_hitCount_total Rundeck gauges metrics
  # TYPE rundeck_services_AuthorizationService_sourceCache_hitCount_total counter
  rundeck_services_AuthorizationService_sourceCache_hitCount_total{instance_address="localhost:4440"} 0.0
  # HELP rundeck_services_AuthorizationService_sourceCache_loadExceptionCount_total Rundeck gauges metrics
  # TYPE rundeck_services_AuthorizationService_sourceCache_loadExceptionCount_total counter
  rundeck_services_AuthorizationService_sourceCache_loadExceptionCount_total{instance_address="localhost:4440"} 0.0
  # HELP rundeck_services_AuthorizationService_sourceCache_missCount_total Rundeck gauges metrics
  # TYPE rundeck_services_AuthorizationService_sourceCache_missCount_total counter
  rundeck_services_AuthorizationService_sourceCache_missCount_total{instance_address="localhost:4440"} 0.0
  # HELP rundeck_services_NodeService_nodeCache_evictionCount_total Rundeck gauges metrics
  # TYPE rundeck_services_NodeService_nodeCache_evictionCount_total counter
  rundeck_services_NodeService_nodeCache_evictionCount_total{instance_address="localhost:4440"} 0.0
  # HELP rundeck_services_NodeService_nodeCache_hitCount_total Rundeck gauges metrics
  # TYPE rundeck_services_NodeService_nodeCache_hitCount_total counter
  rundeck_services_NodeService_nodeCache_hitCount_total{instance_address="localhost:4440"} 182.0
  # HELP rundeck_services_NodeService_nodeCache_loadExceptionCount_total Rundeck gauges metrics
  # TYPE rundeck_services_NodeService_nodeCache_loadExceptionCount_total counter
  rundeck_services_NodeService_nodeCache_loadExceptionCount_total{instance_address="localhost:4440"} 0.0
  # HELP rundeck_services_NodeService_nodeCache_missCount_total Rundeck gauges metrics
  # TYPE rundeck_services_NodeService_nodeCache_missCount_total counter
  rundeck_services_NodeService_nodeCache_missCount_total{instance_address="localhost:4440"} 10.0
  # HELP rundeck_services_ProjectManagerService_fileCache_evictionCount_total Rundeck gauges metrics
  # TYPE rundeck_services_ProjectManagerService_fileCache_evictionCount_total counter
  rundeck_services_ProjectManagerService_fileCache_evictionCount_total{instance_address="localhost:4440"} 0.0
  # HELP rundeck_services_ProjectManagerService_fileCache_hitCount_total Rundeck gauges metrics
  # TYPE rundeck_services_ProjectManagerService_fileCache_hitCount_total counter
  rundeck_services_ProjectManagerService_fileCache_hitCount_total{instance_address="localhost:4440"} 0.0
  # HELP rundeck_services_ProjectManagerService_fileCache_loadExceptionCount_total Rundeck gauges metrics
  # TYPE rundeck_services_ProjectManagerService_fileCache_loadExceptionCount_total counter
  rundeck_services_ProjectManagerService_fileCache_loadExceptionCount_total{instance_address="localhost:4440"} 0.0
  # HELP rundeck_services_ProjectManagerService_fileCache_missCount_total Rundeck gauges metrics
  # TYPE rundeck_services_ProjectManagerService_fileCache_missCount_total counter
  rundeck_services_ProjectManagerService_fileCache_missCount_total{instance_address="localhost:4440"} 0.0
  # HELP rundeck_services_ProjectManagerService_projectCache_evictionCount_total Rundeck gauges metrics
  # TYPE rundeck_services_ProjectManagerService_projectCache_evictionCount_total counter
  rundeck_services_ProjectManagerService_projectCache_evictionCount_total{instance_address="localhost:4440"} 0.0
  # HELP rundeck_services_ProjectManagerService_projectCache_hitCount_total Rundeck gauges metrics
  # TYPE rundeck_services_ProjectManagerService_projectCache_hitCount_total counter
  rundeck_services_ProjectManagerService_projectCache_hitCount_total{instance_address="localhost:4440"} 5124.0
  # HELP rundeck_services_ProjectManagerService_projectCache_loadExceptionCount_total Rundeck gauges metrics
  # TYPE rundeck_services_ProjectManagerService_projectCache_loadExceptionCount_total counter
  rundeck_services_ProjectManagerService_projectCache_loadExceptionCount_total{instance_address="localhost:4440"} 0.0
  # HELP rundeck_services_ProjectManagerService_projectCache_missCount_total Rundeck gauges metrics
  # TYPE rundeck_services_ProjectManagerService_projectCache_missCount_total counter
  rundeck_services_ProjectManagerService_projectCache_missCount_total{instance_address="localhost:4440"} 2.0
  # HELP rundeck_scheduler_quartz_scheduledJobs Rundeck counters metrics
  # TYPE rundeck_scheduler_quartz_scheduledJobs gauge
  rundeck_scheduler_quartz_scheduledJobs{instance_address="localhost:4440"} 8.0
  # HELP rundeck_services_AuthorizationService_systemAuthorization_evaluateMeter_total Rundeck meters metrics
  # TYPE rundeck_services_AuthorizationService_systemAuthorization_evaluateMeter_total counter
  rundeck_services_AuthorizationService_systemAuthorization_evaluateMeter_total{instance_address="localhost:4440"} 2.0
  # HELP rundeck_services_AuthorizationService_systemAuthorization_evaluateSetMeter_total Rundeck meters metrics
  # TYPE rundeck_services_AuthorizationService_systemAuthorization_evaluateSetMeter_total counter
  rundeck_services_AuthorizationService_systemAuthorization_evaluateSetMeter_total{instance_address="localhost:4440"} 0.0
  # HELP rundeck_services_ExecutionService_executionFailureMeter_total Rundeck meters metrics
  # TYPE rundeck_services_ExecutionService_executionFailureMeter_total counter
  rundeck_services_ExecutionService_executionFailureMeter_total{instance_address="localhost:4440"} 37.0
  # HELP rundeck_services_ExecutionService_executionJobStartMeter_total Rundeck meters metrics
  # TYPE rundeck_services_ExecutionService_executionJobStartMeter_total counter
  rundeck_services_ExecutionService_executionJobStartMeter_total{instance_address="localhost:4440"} 64.0
  # HELP rundeck_services_ExecutionService_executionStartMeter_total Rundeck meters metrics
  # TYPE rundeck_services_ExecutionService_executionStartMeter_total counter
  rundeck_services_ExecutionService_executionStartMeter_total{instance_address="localhost:4440"} 64.0
  # HELP rundeck_services_ExecutionService_executionSuccessMeter_total Rundeck meters metrics
  # TYPE rundeck_services_ExecutionService_executionSuccessMeter_total counter
  rundeck_services_ExecutionService_executionSuccessMeter_total{instance_address="localhost:4440"} 27.0
  # HELP rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectResource_total Rundeck timers metrics
  # TYPE rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectResource_total counter
  rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectResource_total{instance_address="localhost:4440"} 2.0
  # HELP rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_filterAuthorizedProjectExecutionsAll_total Rundeck timers metrics
  # TYPE rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_filterAuthorizedProjectExecutionsAll_total counter
  rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_filterAuthorizedProjectExecutionsAll_total{instance_address="localhost:4440"} 2.0
  # HELP rundeck_api_requests_requestTimer_total Rundeck timers metrics
  # TYPE rundeck_api_requests_requestTimer_total counter
  rundeck_api_requests_requestTimer_total{instance_address="localhost:4440"} 22.0
  # HELP rundeck_controllers_MenuController_apiExecutionsRunningv14_queryQueue_total Rundeck timers metrics
  # TYPE rundeck_controllers_MenuController_apiExecutionsRunningv14_queryQueue_total counter
  rundeck_controllers_MenuController_apiExecutionsRunningv14_queryQueue_total{instance_address="localhost:4440"} 2.0
  # HELP rundeck_quartzjobs_ExecutionJob_executionTimer_total Rundeck timers metrics
  # TYPE rundeck_quartzjobs_ExecutionJob_executionTimer_total counter
  rundeck_quartzjobs_ExecutionJob_executionTimer_total{instance_address="localhost:4440"} 1602.0
  # HELP rundeck_services_AuthorizationService_getSystemAuthorization_total Rundeck timers metrics
  # TYPE rundeck_services_AuthorizationService_getSystemAuthorization_total counter
  rundeck_services_AuthorizationService_getSystemAuthorization_total{instance_address="localhost:4440"} 3241.0
  # HELP rundeck_services_AuthorizationService_systemAuthorization_evaluateSetTimer_total Rundeck timers metrics
  # TYPE rundeck_services_AuthorizationService_systemAuthorization_evaluateSetTimer_total counter
  rundeck_services_AuthorizationService_systemAuthorization_evaluateSetTimer_total{instance_address="localhost:4440"} 0.0
  # HELP rundeck_services_AuthorizationService_systemAuthorization_evaluateTimer_total Rundeck timers metrics
  # TYPE rundeck_services_AuthorizationService_systemAuthorization_evaluateTimer_total counter
  rundeck_services_AuthorizationService_systemAuthorization_evaluateTimer_total{instance_address="localhost:4440"} 2.0
  # HELP rundeck_services_FrameworkService_filterNodeSet_total Rundeck timers metrics
  # TYPE rundeck_services_FrameworkService_filterNodeSet_total counter
  rundeck_services_FrameworkService_filterNodeSet_total{instance_address="localhost:4440"} 192.0
  # HELP rundeck_services_NodeService_project_Test_loadNodes_total Rundeck timers metrics
  # TYPE rundeck_services_NodeService_project_Test_loadNodes_total counter
  rundeck_services_NodeService_project_Test_loadNodes_total{instance_address="localhost:4440"} 8.0
  # HELP rundeck_web_requests_requestTimer_total Rundeck timers metrics
  # TYPE rundeck_web_requests_requestTimer_total counter
  rundeck_web_requests_requestTimer_total{instance_address="localhost:4440"} 22.0
  # HELP rundeck_project_start_timestamp Rundeck Project Test Start Timestamp
  # TYPE rundeck_project_start_timestamp gauge
  rundeck_project_start_timestamp{execution_id="7378",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="f062ab2b-ac23-45a7-81fd-825bbb108afe",job_name="Fail after 120s",project_name="Test",user="admin"} 1.646482200032e+012
  # HELP rundeck_project_execution_duration_seconds Rundeck Project Test Execution Duration
  # TYPE rundeck_project_execution_duration_seconds gauge
  rundeck_project_execution_duration_seconds{execution_id="7378",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="f062ab2b-ac23-45a7-81fd-825bbb108afe",job_name="Fail after 120s",project_name="Test",user="admin"} 120108.0
  # HELP rundeck_project_execution_status Rundeck Project Test Execution Status
  # TYPE rundeck_project_execution_status gauge
  rundeck_project_execution_status{execution_id="7378",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="f062ab2b-ac23-45a7-81fd-825bbb108afe",job_name="Fail after 120s",project_name="Test",status="succeeded",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7378",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="f062ab2b-ac23-45a7-81fd-825bbb108afe",job_name="Fail after 120s",project_name="Test",status="running",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7378",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="f062ab2b-ac23-45a7-81fd-825bbb108afe",job_name="Fail after 120s",project_name="Test",status="failed",user="admin"} 1.0
  rundeck_project_execution_status{execution_id="7378",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="f062ab2b-ac23-45a7-81fd-825bbb108afe",job_name="Fail after 120s",project_name="Test",status="aborted",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7378",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="f062ab2b-ac23-45a7-81fd-825bbb108afe",job_name="Fail after 120s",project_name="Test",status="unknown",user="admin"} 0.0
  # HELP rundeck_project_start_timestamp Rundeck Project Test Start Timestamp
  # TYPE rundeck_project_start_timestamp gauge
  rundeck_project_start_timestamp{execution_id="7380",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="8ebf87b0-dd93-47fb-9e9e-7c5fc628a511",job_name="Fail after 90s",project_name="Test",user="admin"} 1.646482200048e+012
  # HELP rundeck_project_execution_duration_seconds Rundeck Project Test Execution Duration
  # TYPE rundeck_project_execution_duration_seconds gauge
  rundeck_project_execution_duration_seconds{execution_id="7380",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="8ebf87b0-dd93-47fb-9e9e-7c5fc628a511",job_name="Fail after 90s",project_name="Test",user="admin"} 90110.0
  # HELP rundeck_project_execution_status Rundeck Project Test Execution Status
  # TYPE rundeck_project_execution_status gauge
  rundeck_project_execution_status{execution_id="7380",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="8ebf87b0-dd93-47fb-9e9e-7c5fc628a511",job_name="Fail after 90s",project_name="Test",status="succeeded",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7380",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="8ebf87b0-dd93-47fb-9e9e-7c5fc628a511",job_name="Fail after 90s",project_name="Test",status="running",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7380",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="8ebf87b0-dd93-47fb-9e9e-7c5fc628a511",job_name="Fail after 90s",project_name="Test",status="failed",user="admin"} 1.0
  rundeck_project_execution_status{execution_id="7380",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="8ebf87b0-dd93-47fb-9e9e-7c5fc628a511",job_name="Fail after 90s",project_name="Test",status="aborted",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7380",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="8ebf87b0-dd93-47fb-9e9e-7c5fc628a511",job_name="Fail after 90s",project_name="Test",status="unknown",user="admin"} 0.0
  # HELP rundeck_project_start_timestamp Rundeck Project Test Start Timestamp
  # TYPE rundeck_project_start_timestamp gauge
  rundeck_project_start_timestamp{execution_id="7388",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="fff6e7b1-4fdd-467b-b807-e168f9ee8865",job_name="Success after 15s",project_name="Test",user="admin"} 1.646482248021e+012
  # HELP rundeck_project_execution_duration_seconds Rundeck Project Test Execution Duration
  # TYPE rundeck_project_execution_duration_seconds gauge
  rundeck_project_execution_duration_seconds{execution_id="7388",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="fff6e7b1-4fdd-467b-b807-e168f9ee8865",job_name="Success after 15s",project_name="Test",user="admin"} 15334.0
  # HELP rundeck_project_execution_status Rundeck Project Test Execution Status
  # TYPE rundeck_project_execution_status gauge
  rundeck_project_execution_status{execution_id="7388",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="fff6e7b1-4fdd-467b-b807-e168f9ee8865",job_name="Success after 15s",project_name="Test",status="succeeded",user="admin"} 1.0
  rundeck_project_execution_status{execution_id="7388",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="fff6e7b1-4fdd-467b-b807-e168f9ee8865",job_name="Success after 15s",project_name="Test",status="running",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7388",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="fff6e7b1-4fdd-467b-b807-e168f9ee8865",job_name="Success after 15s",project_name="Test",status="failed",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7388",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="fff6e7b1-4fdd-467b-b807-e168f9ee8865",job_name="Success after 15s",project_name="Test",status="aborted",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7388",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="fff6e7b1-4fdd-467b-b807-e168f9ee8865",job_name="Success after 15s",project_name="Test",status="unknown",user="admin"} 0.0
  # HELP rundeck_project_start_timestamp Rundeck Project Test Start Timestamp
  # TYPE rundeck_project_start_timestamp gauge
  rundeck_project_start_timestamp{execution_id="7387",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="e4a5400d-117b-4b76-9f8c-8e8a0eca76e8",job_name="Fail after 15s",project_name="Test",user="admin"} 1.646482248018e+012
  # HELP rundeck_project_execution_duration_seconds Rundeck Project Test Execution Duration
  # TYPE rundeck_project_execution_duration_seconds gauge
  rundeck_project_execution_duration_seconds{execution_id="7387",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="e4a5400d-117b-4b76-9f8c-8e8a0eca76e8",job_name="Fail after 15s",project_name="Test",user="admin"} 15089.0
  # HELP rundeck_project_execution_status Rundeck Project Test Execution Status
  # TYPE rundeck_project_execution_status gauge
  rundeck_project_execution_status{execution_id="7387",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="e4a5400d-117b-4b76-9f8c-8e8a0eca76e8",job_name="Fail after 15s",project_name="Test",status="succeeded",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7387",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="e4a5400d-117b-4b76-9f8c-8e8a0eca76e8",job_name="Fail after 15s",project_name="Test",status="running",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7387",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="e4a5400d-117b-4b76-9f8c-8e8a0eca76e8",job_name="Fail after 15s",project_name="Test",status="failed",user="admin"} 1.0
  rundeck_project_execution_status{execution_id="7387",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="e4a5400d-117b-4b76-9f8c-8e8a0eca76e8",job_name="Fail after 15s",project_name="Test",status="aborted",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7387",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="e4a5400d-117b-4b76-9f8c-8e8a0eca76e8",job_name="Fail after 15s",project_name="Test",status="unknown",user="admin"} 0.0
  # HELP rundeck_project_start_timestamp Rundeck Project Test Start Timestamp
  # TYPE rundeck_project_start_timestamp gauge
  rundeck_project_start_timestamp{execution_id="7383",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="5fb2705f-73bb-4bdc-a158-b5f046e3b474",job_name="Success after 30s",project_name="Test",user="admin"} 1.646482231023e+012
  # HELP rundeck_project_execution_duration_seconds Rundeck Project Test Execution Duration
  # TYPE rundeck_project_execution_duration_seconds gauge
  rundeck_project_execution_duration_seconds{execution_id="7383",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="5fb2705f-73bb-4bdc-a158-b5f046e3b474",job_name="Success after 30s",project_name="Test",user="admin"} 30320.0
  # HELP rundeck_project_execution_status Rundeck Project Test Execution Status
  # TYPE rundeck_project_execution_status gauge
  rundeck_project_execution_status{execution_id="7383",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="5fb2705f-73bb-4bdc-a158-b5f046e3b474",job_name="Success after 30s",project_name="Test",status="succeeded",user="admin"} 1.0
  rundeck_project_execution_status{execution_id="7383",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="5fb2705f-73bb-4bdc-a158-b5f046e3b474",job_name="Success after 30s",project_name="Test",status="running",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7383",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="5fb2705f-73bb-4bdc-a158-b5f046e3b474",job_name="Success after 30s",project_name="Test",status="failed",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7383",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="5fb2705f-73bb-4bdc-a158-b5f046e3b474",job_name="Success after 30s",project_name="Test",status="aborted",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7383",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="5fb2705f-73bb-4bdc-a158-b5f046e3b474",job_name="Success after 30s",project_name="Test",status="unknown",user="admin"} 0.0
  # HELP rundeck_project_start_timestamp Rundeck Project Test Start Timestamp
  # TYPE rundeck_project_start_timestamp gauge
  rundeck_project_start_timestamp{execution_id="7384",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="a5d6a578-50fe-4d4f-ae40-77eff506ea02",job_name="Fail after 30s",project_name="Test",user="admin"} 1.646482231025e+012
  # HELP rundeck_project_execution_duration_seconds Rundeck Project Test Execution Duration
  # TYPE rundeck_project_execution_duration_seconds gauge
  rundeck_project_execution_duration_seconds{execution_id="7384",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="a5d6a578-50fe-4d4f-ae40-77eff506ea02",job_name="Fail after 30s",project_name="Test",user="admin"} 30065.0
  # HELP rundeck_project_execution_status Rundeck Project Test Execution Status
  # TYPE rundeck_project_execution_status gauge
  rundeck_project_execution_status{execution_id="7384",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="a5d6a578-50fe-4d4f-ae40-77eff506ea02",job_name="Fail after 30s",project_name="Test",status="succeeded",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7384",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="a5d6a578-50fe-4d4f-ae40-77eff506ea02",job_name="Fail after 30s",project_name="Test",status="running",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7384",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="a5d6a578-50fe-4d4f-ae40-77eff506ea02",job_name="Fail after 30s",project_name="Test",status="failed",user="admin"} 1.0
  rundeck_project_execution_status{execution_id="7384",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="a5d6a578-50fe-4d4f-ae40-77eff506ea02",job_name="Fail after 30s",project_name="Test",status="aborted",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7384",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="a5d6a578-50fe-4d4f-ae40-77eff506ea02",job_name="Fail after 30s",project_name="Test",status="unknown",user="admin"} 0.0
  # HELP rundeck_project_start_timestamp Rundeck Project Test Start Timestamp
  # TYPE rundeck_project_start_timestamp gauge
  rundeck_project_start_timestamp{execution_id="7376",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="dcba57e3-6d2c-4127-8401-21382079bf5e",job_name="Success after 60s",project_name="Test",user="admin"} 1.646482200029e+012
  # HELP rundeck_project_execution_duration_seconds Rundeck Project Test Execution Duration
  # TYPE rundeck_project_execution_duration_seconds gauge
  rundeck_project_execution_duration_seconds{execution_id="7376",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="dcba57e3-6d2c-4127-8401-21382079bf5e",job_name="Success after 60s",project_name="Test",user="admin"} 60384.0
  # HELP rundeck_project_execution_status Rundeck Project Test Execution Status
  # TYPE rundeck_project_execution_status gauge
  rundeck_project_execution_status{execution_id="7376",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="dcba57e3-6d2c-4127-8401-21382079bf5e",job_name="Success after 60s",project_name="Test",status="succeeded",user="admin"} 1.0
  rundeck_project_execution_status{execution_id="7376",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="dcba57e3-6d2c-4127-8401-21382079bf5e",job_name="Success after 60s",project_name="Test",status="running",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7376",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="dcba57e3-6d2c-4127-8401-21382079bf5e",job_name="Success after 60s",project_name="Test",status="failed",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7376",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="dcba57e3-6d2c-4127-8401-21382079bf5e",job_name="Success after 60s",project_name="Test",status="aborted",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7376",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="dcba57e3-6d2c-4127-8401-21382079bf5e",job_name="Success after 60s",project_name="Test",status="unknown",user="admin"} 0.0
  # HELP rundeck_project_start_timestamp Rundeck Project Test Start Timestamp
  # TYPE rundeck_project_start_timestamp gauge
  rundeck_project_start_timestamp{execution_id="7375",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="3fcc1617-74d4-422b-b7cf-bd3123b3f97c",job_name="Fail after 60s",project_name="Test",user="admin"} 1.646482200027e+012
  # HELP rundeck_project_execution_duration_seconds Rundeck Project Test Execution Duration
  # TYPE rundeck_project_execution_duration_seconds gauge
  rundeck_project_execution_duration_seconds{execution_id="7375",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="3fcc1617-74d4-422b-b7cf-bd3123b3f97c",job_name="Fail after 60s",project_name="Test",user="admin"} 60136.0
  # HELP rundeck_project_execution_status Rundeck Project Test Execution Status
  # TYPE rundeck_project_execution_status gauge
  rundeck_project_execution_status{execution_id="7375",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="3fcc1617-74d4-422b-b7cf-bd3123b3f97c",job_name="Fail after 60s",project_name="Test",status="succeeded",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7375",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="3fcc1617-74d4-422b-b7cf-bd3123b3f97c",job_name="Fail after 60s",project_name="Test",status="running",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7375",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="3fcc1617-74d4-422b-b7cf-bd3123b3f97c",job_name="Fail after 60s",project_name="Test",status="failed",user="admin"} 1.0
  rundeck_project_execution_status{execution_id="7375",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="3fcc1617-74d4-422b-b7cf-bd3123b3f97c",job_name="Fail after 60s",project_name="Test",status="aborted",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="7375",execution_type="scheduled",instance_address="localhost:4440",job_group="",job_id="3fcc1617-74d4-422b-b7cf-bd3123b3f97c",job_name="Fail after 60s",project_name="Test",status="unknown",user="admin"} 0.0
  # HELP rundeck_project_executions_total Rundeck Project ProjectName Total Executions
  # TYPE rundeck_project_executions_total counter
  rundeck_project_executions_total{instance_address="localhost:4440",project_name="Test"} 300.0

  ```
</details>

#### Running with Docker

```sh
docker build -t rundeck_exporter .

docker run --rm -d -p 9620:9620 -e RUNDECK_TOKEN=$RUNDECK_TOKEN rundeck_exporter \
--host 0.0.0.0 \
--rundeck.url https://rundeck.test.com \
--rundeck.skip_ssl
```
#### Running with Docker-Compose

```sh
cd examples/docker-compose
docker-compose up -d
```

Docker Compose services:
- Rundeck - http://localhost:4440
- Rundeck Exporter - http://localhost:9620
- Prometheus - http://localhost:9090 (already configured to scrape rundeck_exporter metrics)
- Grafana - http://localhost:3000 (already configured with Prometheus Datasource and Rundeck Dashboard)

After provisioning of the docker-compose services, access Rundeck from http://localhost:4440/user/profile and gerate a new API token. Place the token at **RUNDECK_TOKEN** environment variable in the **docker-compose.yml** and run `docker-compose up -d` again.
