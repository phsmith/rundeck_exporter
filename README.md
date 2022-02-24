## Rundeck_Exporter

![Docker Pulls](https://img.shields.io/docker/pulls/phsmith/rundeck-exporter?logo=docker&)

Rundeck Metrics Exporter for Prometheus.

![Rundeck-Grafana-Dashboard](examples/grafana/Rundeck-Grafana-Dashboard.png)

*Dashboard example can be found in: [examples/grafana](examples/grafana)*

This exporter uses the prometheus_client and requests Python module to expose Rundeck metrics found in:

 * RUNDECK_URL/*api_version*/system/info
 * RUNDECK_URL/*api_version*/metrics/metrics

 Where *version* represents the Rundeck API version, like: 31,32,33,34,etc.

 This code was tested on Rundeck API version 31+.

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

Rundeck token must be passed as a environment variable (RUNDECK_TOKEN) to work.

The rundeck_exporter supports the following paramenters:

```
$ ./rundeck_exporter.py --help

usage: rundeck_exporter.py [-h] [--debug] [-v] [--host RUNDECK_EXPORTER_HOST] [--port RUNDECK_EXPORTER_PORT] [--rundeck.url RUNDECK_URL] [--rundeck.skip_ssl]
                           [--rundeck.api.version RUNDECK_API_VERSION] [--rundeck.username RUNDECK_USERNAME] [--rundeck.projects.executions]
                           [--rundeck.projects.filter RUNDECK_PROJECTS_FILTER [RUNDECK_PROJECTS_FILTER ...]] [--rundeck.projects.executions.cache]
                           [--rundeck.cached.requests.ttl RUNDECK_CACHED_REQUESTS_TTL] [--rundeck.cpu.stats] [--rundeck.memory.stats]

Rundeck Metrics Exporter

required environment vars:
    RUNDECK_TOKEN        Rundeck API Token
    RUNDECK_USERPASSWORD Rundeck User Password (rundeck.username is needed too)
                         to retrieve data from /metrics/metrics
                         from Rundeck with API versions older than 25

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
  --rundeck.projects.filter RUNDECK_PROJECTS_FILTER [RUNDECK_PROJECTS_FILTER ...]
                        Get executions only from listed projects (delimiter = space).
  --rundeck.projects.executions.cache
                        Cache requests for project executions metrics query.
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
| RUNDECK_API_VERSION | Default: 31 | Rundeck API version. |
| RUNDECK_SKIP_SSL | <ul><li>True</li><li>False (default)</li></ul> | Skip SSL certificate check. |
| RUNDECK_PROJECTS_EXECUTIONS | <ul><li>True</li><li>False (default)</li></ul> | Get projects executions metrics. |
| RUNDECK_PROJECTS_FILTER | [] | Get executions only from listed projects. |
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

  ...
  # HELP python_gc_objects_collected_total Objects collected during gc
  # TYPE python_gc_objects_collected_total counter
  python_gc_objects_collected_total{generation="0"} 422.0
  python_gc_objects_collected_total{generation="1"} 48.0
  python_gc_objects_collected_total{generation="2"} 0.0
  # HELP python_gc_objects_uncollectable_total Uncollectable object found during GC
  # TYPE python_gc_objects_uncollectable_total counter
  python_gc_objects_uncollectable_total{generation="0"} 0.0
  python_gc_objects_uncollectable_total{generation="1"} 0.0
  python_gc_objects_uncollectable_total{generation="2"} 0.0
  # HELP python_gc_collections_total Number of times this generation was collected
  # TYPE python_gc_collections_total counter
  python_gc_collections_total{generation="0"} 55.0
  python_gc_collections_total{generation="1"} 5.0
  python_gc_collections_total{generation="2"} 0.0
  # HELP python_info Python platform information
  # TYPE python_info gauge
  python_info{implementation="CPython",major="3",minor="9",patchlevel="6",version="3.9.6"} 1.0
  # HELP process_virtual_memory_bytes Virtual memory size in bytes.
  # TYPE process_virtual_memory_bytes gauge
  process_virtual_memory_bytes 2.760704e+07
  # HELP process_resident_memory_bytes Resident memory size in bytes.
  # TYPE process_resident_memory_bytes gauge
  process_resident_memory_bytes 2.2212608e+07
  # HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
  # TYPE process_start_time_seconds gauge
  process_start_time_seconds 1.63619872136e+09
  # HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
  # TYPE process_cpu_seconds_total counter
  process_cpu_seconds_total 1.48
  # HELP process_open_fds Number of open file descriptors.
  # TYPE process_open_fds gauge
  process_open_fds 6.0
  # HELP process_max_fds Maximum number of open file descriptors.
  # TYPE process_max_fds gauge
  process_max_fds 1.048576e+06
  # HELP rundeck_system_info Rundeck system info
  # TYPE rundeck_system_info gauge
  rundeck_system_info{apiversion="40",base="/home/rundeck",build="3.4.3-20210823",buildGit="v3.4.3-0-gb636681",node="2b2f735826c9",serverUUID="a14bc3e6-75e8-4fe4-a90d-a16dcc976bf6",version="3.4.3-20210823"} 1.0
  # HELP rundeck_system_stats_uptime_since Rundeck system stats
  # TYPE rundeck_system_stats_uptime_since gauge
  rundeck_system_stats_uptime_since 1.636164386186e+012
  # HELP rundeck_system_stats_cpu_loadAverage_ratio Rundeck system stats
  # TYPE rundeck_system_stats_cpu_loadAverage_ratio gauge
  rundeck_system_stats_cpu_loadAverage_ratio 2.95
  # HELP rundeck_system_stats_memory_max_bytes Rundeck system stats
  # TYPE rundeck_system_stats_memory_max_bytes gauge
  rundeck_system_stats_memory_max_bytes 1.2438208512e+010
  # HELP rundeck_system_stats_memory_free_bytes Rundeck system stats
  # TYPE rundeck_system_stats_memory_free_bytes gauge
  rundeck_system_stats_memory_free_bytes 5.10558448e+08
  # HELP rundeck_system_stats_memory_total_bytes Rundeck system stats
  # TYPE rundeck_system_stats_memory_total_bytes gauge
  rundeck_system_stats_memory_total_bytes 1.239416832e+09
  # HELP rundeck_system_stats_scheduler_running Rundeck system stats
  # TYPE rundeck_system_stats_scheduler_running gauge
  rundeck_system_stats_scheduler_running 1.0
  # HELP rundeck_system_stats_scheduler_threadPoolSize Rundeck system stats
  # TYPE rundeck_system_stats_scheduler_threadPoolSize gauge
  rundeck_system_stats_scheduler_threadPoolSize 10.0
  # HELP rundeck_system_stats_threads_active Rundeck system stats
  # TYPE rundeck_system_stats_threads_active gauge
  rundeck_system_stats_threads_active 50.0
  # HELP rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_evictionCount Rundeck gauges metrics
  # TYPE rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_evictionCount gauge
  rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_evictionCount 0.0
  # HELP rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_hitCount Rundeck gauges metrics
  # TYPE rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_hitCount gauge
  rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_hitCount 0.0
  # HELP rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_loadExceptionCount Rundeck gauges metrics
  # TYPE rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_loadExceptionCount gauge
  rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_loadExceptionCount 0.0
  # HELP rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_missCount Rundeck gauges metrics
  # TYPE rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_missCount gauge
  rundeck_com_dtolabs_rundeck_server_AuthContextEvaluatorCacheManager_authContextEvaluatorCache_missCount 0.0
  # HELP rundeck_dataSource_connection_pingTime Rundeck gauges metrics
  # TYPE rundeck_dataSource_connection_pingTime gauge
  rundeck_dataSource_connection_pingTime 0.0
  # HELP rundeck_scheduler_quartz_runningExecutions Rundeck gauges metrics
  # TYPE rundeck_scheduler_quartz_runningExecutions gauge
  rundeck_scheduler_quartz_runningExecutions 1.0
  # HELP rundeck_services_AuthorizationService_sourceCache_evictionCount_total Rundeck gauges metrics
  # TYPE rundeck_services_AuthorizationService_sourceCache_evictionCount_total counter
  rundeck_services_AuthorizationService_sourceCache_evictionCount_total 0.0
  # HELP rundeck_services_AuthorizationService_sourceCache_hitCount_total Rundeck gauges metrics
  # TYPE rundeck_services_AuthorizationService_sourceCache_hitCount_total counter
  rundeck_services_AuthorizationService_sourceCache_hitCount_total 0.0
  # HELP rundeck_services_AuthorizationService_sourceCache_loadExceptionCount_total Rundeck gauges metrics
  # TYPE rundeck_services_AuthorizationService_sourceCache_loadExceptionCount_total counter
  rundeck_services_AuthorizationService_sourceCache_loadExceptionCount_total 0.0
  # HELP rundeck_services_AuthorizationService_sourceCache_missCount_total Rundeck gauges metrics
  # TYPE rundeck_services_AuthorizationService_sourceCache_missCount_total counter
  rundeck_services_AuthorizationService_sourceCache_missCount_total 0.0
  # HELP rundeck_services_NodeService_nodeCache_evictionCount_total Rundeck gauges metrics
  # TYPE rundeck_services_NodeService_nodeCache_evictionCount_total counter
  rundeck_services_NodeService_nodeCache_evictionCount_total 0.0
  # HELP rundeck_services_NodeService_nodeCache_hitCount_total Rundeck gauges metrics
  # TYPE rundeck_services_NodeService_nodeCache_hitCount_total counter
  rundeck_services_NodeService_nodeCache_hitCount_total 23879.0
  # HELP rundeck_services_NodeService_nodeCache_loadExceptionCount_total Rundeck gauges metrics
  # TYPE rundeck_services_NodeService_nodeCache_loadExceptionCount_total counter
  rundeck_services_NodeService_nodeCache_loadExceptionCount_total 0.0
  # HELP rundeck_services_NodeService_nodeCache_missCount_total Rundeck gauges metrics
  # TYPE rundeck_services_NodeService_nodeCache_missCount_total counter
  rundeck_services_NodeService_nodeCache_missCount_total 6.0
  # HELP rundeck_services_ProjectManagerService_fileCache_evictionCount_total Rundeck gauges metrics
  # TYPE rundeck_services_ProjectManagerService_fileCache_evictionCount_total counter
  rundeck_services_ProjectManagerService_fileCache_evictionCount_total 0.0
  # HELP rundeck_services_ProjectManagerService_fileCache_hitCount_total Rundeck gauges metrics
  # TYPE rundeck_services_ProjectManagerService_fileCache_hitCount_total counter
  rundeck_services_ProjectManagerService_fileCache_hitCount_total 110.0
  # HELP rundeck_services_ProjectManagerService_fileCache_loadExceptionCount_total Rundeck gauges metrics
  # TYPE rundeck_services_ProjectManagerService_fileCache_loadExceptionCount_total counter
  rundeck_services_ProjectManagerService_fileCache_loadExceptionCount_total 0.0
  # HELP rundeck_services_ProjectManagerService_fileCache_missCount_total Rundeck gauges metrics
  # TYPE rundeck_services_ProjectManagerService_fileCache_missCount_total counter
  rundeck_services_ProjectManagerService_fileCache_missCount_total 4.0
  # HELP rundeck_services_ProjectManagerService_projectCache_evictionCount_total Rundeck gauges metrics
  # TYPE rundeck_services_ProjectManagerService_projectCache_evictionCount_total counter
  rundeck_services_ProjectManagerService_projectCache_evictionCount_total 0.0
  # HELP rundeck_services_ProjectManagerService_projectCache_hitCount_total Rundeck gauges metrics
  # TYPE rundeck_services_ProjectManagerService_projectCache_hitCount_total counter
  rundeck_services_ProjectManagerService_projectCache_hitCount_total 332804.0
  # HELP rundeck_services_ProjectManagerService_projectCache_loadExceptionCount_total Rundeck gauges metrics
  # TYPE rundeck_services_ProjectManagerService_projectCache_loadExceptionCount_total counter
  rundeck_services_ProjectManagerService_projectCache_loadExceptionCount_total 0.0
  # HELP rundeck_services_ProjectManagerService_projectCache_missCount_total Rundeck gauges metrics
  # TYPE rundeck_services_ProjectManagerService_projectCache_missCount_total counter
  rundeck_services_ProjectManagerService_projectCache_missCount_total 6.0
  # HELP rundeck_scheduler_quartz_scheduledJobs Rundeck counters metrics
  # TYPE rundeck_scheduler_quartz_scheduledJobs gauge
  rundeck_scheduler_quartz_scheduledJobs 7.0
  # HELP rundeck_controllers_FrameworkController_createProjectPost_total Rundeck meters metrics
  # TYPE rundeck_controllers_FrameworkController_createProjectPost_total counter
  rundeck_controllers_FrameworkController_createProjectPost_total 2.0
  # HELP rundeck_services_AuthorizationService_systemAuthorization_evaluateMeter_total Rundeck meters metrics
  # TYPE rundeck_services_AuthorizationService_systemAuthorization_evaluateMeter_total counter
  rundeck_services_AuthorizationService_systemAuthorization_evaluateMeter_total 110.0
  # HELP rundeck_services_AuthorizationService_systemAuthorization_evaluateSetMeter_total Rundeck meters metrics
  # TYPE rundeck_services_AuthorizationService_systemAuthorization_evaluateSetMeter_total counter
  rundeck_services_AuthorizationService_systemAuthorization_evaluateSetMeter_total 367.0
  # HELP rundeck_services_ExecutionService_executionFailureMeter_total Rundeck meters metrics
  # TYPE rundeck_services_ExecutionService_executionFailureMeter_total counter
  rundeck_services_ExecutionService_executionFailureMeter_total 6591.0
  # HELP rundeck_services_ExecutionService_executionJobStartMeter_total Rundeck meters metrics
  # TYPE rundeck_services_ExecutionService_executionJobStartMeter_total counter
  rundeck_services_ExecutionService_executionJobStartMeter_total 7957.0
  # HELP rundeck_services_ExecutionService_executionStartMeter_total Rundeck meters metrics
  # TYPE rundeck_services_ExecutionService_executionStartMeter_total counter
  rundeck_services_ExecutionService_executionStartMeter_total 7957.0
  # HELP rundeck_services_ExecutionService_executionSuccessMeter_total Rundeck meters metrics
  # TYPE rundeck_services_ExecutionService_executionSuccessMeter_total counter
  rundeck_services_ExecutionService_executionSuccessMeter_total 1365.0
  # HELP rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeApplicationResource_total Rundeck timers metrics
  # TYPE rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeApplicationResource_total counter
  rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeApplicationResource_total 6382.0
  # HELP rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeApplicationResourceAll_total Rundeck timers metrics
  # TYPE rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeApplicationResourceAll_total counter
  rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeApplicationResourceAll_total 6.0
  # HELP rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeApplicationResourceTypeAll_total Rundeck timers metrics
  # TYPE rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeApplicationResourceTypeAll_total counter
  rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeApplicationResourceTypeAll_total 3.0
  # HELP rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectJobAll_total Rundeck timers metrics
  # TYPE rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectJobAll_total counter
  rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectJobAll_total 5.0
  # HELP rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectResource_total Rundeck timers metrics
  # TYPE rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectResource_total counter
  rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectResource_total 65.0
  # HELP rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectResourceAll_total Rundeck timers metrics
  # TYPE rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectResourceAll_total counter
  rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectResourceAll_total 3163.0
  # HELP rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectResourceAny_total Rundeck timers metrics
  # TYPE rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectResourceAny_total counter
  rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectResourceAny_total 60.0
  # HELP rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectResources_total Rundeck timers metrics
  # TYPE rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectResources_total counter
  rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_authorizeProjectResources_total 18.0
  # HELP rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_filterAuthorizedProjectExecutionsAll_total Rundeck timers metrics
  # TYPE rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_filterAuthorizedProjectExecutionsAll_total counter
  rundeck_org_rundeck_app_authorization_TimedAuthContextEvaluator_filterAuthorizedProjectExecutionsAll_total 3076.0
  # HELP rundeck_api_requests_requestTimer_total Rundeck timers metrics
  # TYPE rundeck_api_requests_requestTimer_total counter
  rundeck_api_requests_requestTimer_total 15111.0
  # HELP rundeck_controllers_MenuController_apiExecutionsRunningv14_queryQueue_total Rundeck timers metrics
  # TYPE rundeck_controllers_MenuController_apiExecutionsRunningv14_queryQueue_total counter
  rundeck_controllers_MenuController_apiExecutionsRunningv14_queryQueue_total 3080.0
  # HELP rundeck_controllers_MenuController_loadSummaryProjectStatsOrig_total Rundeck timers metrics
  # TYPE rundeck_controllers_MenuController_loadSummaryProjectStatsOrig_total counter
  rundeck_controllers_MenuController_loadSummaryProjectStatsOrig_total 5.0
  # HELP rundeck_controllers_ReportsController_index_getExecutionReports_total Rundeck timers metrics
  # TYPE rundeck_controllers_ReportsController_index_getExecutionReports_total counter
  rundeck_controllers_ReportsController_index_getExecutionReports_total 10.0
  # HELP rundeck_quartzjobs_ExecutionJob_executionTimer_total Rundeck timers metrics
  # TYPE rundeck_quartzjobs_ExecutionJob_executionTimer_total counter
  rundeck_quartzjobs_ExecutionJob_executionTimer_total 55634.0
  # HELP rundeck_services_AuthorizationService_getSystemAuthorization_total Rundeck timers metrics
  # TYPE rundeck_services_AuthorizationService_getSystemAuthorization_total counter
  rundeck_services_AuthorizationService_getSystemAuthorization_total 128450.0
  # HELP rundeck_services_AuthorizationService_systemAuthorization_evaluateSetTimer_total Rundeck timers metrics
  # TYPE rundeck_services_AuthorizationService_systemAuthorization_evaluateSetTimer_total counter
  rundeck_services_AuthorizationService_systemAuthorization_evaluateSetTimer_total 367.0
  # HELP rundeck_services_AuthorizationService_systemAuthorization_evaluateTimer_total Rundeck timers metrics
  # TYPE rundeck_services_AuthorizationService_systemAuthorization_evaluateTimer_total counter
  rundeck_services_AuthorizationService_systemAuthorization_evaluateTimer_total 110.0
  # HELP rundeck_services_FrameworkService_filterNodeSet_total Rundeck timers metrics
  # TYPE rundeck_services_FrameworkService_filterNodeSet_total counter
  rundeck_services_FrameworkService_filterNodeSet_total 23876.0
  # HELP rundeck_services_NodeService_project_OtherTest_loadNodes_total Rundeck timers metrics
  # TYPE rundeck_services_NodeService_project_OtherTest_loadNodes_total counter
  rundeck_services_NodeService_project_OtherTest_loadNodes_total 30.0
  # HELP rundeck_services_NodeService_project_Test_loadNodes_total Rundeck timers metrics
  # TYPE rundeck_services_NodeService_project_Test_loadNodes_total counter
  rundeck_services_NodeService_project_Test_loadNodes_total 1092.0
  # HELP rundeck_web_requests_requestTimer_total Rundeck timers metrics
  # TYPE rundeck_web_requests_requestTimer_total counter
  rundeck_web_requests_requestTimer_total 15376.0
  # HELP rundeck_project_start_timestamp Rundeck Project OtherTest Start Timestamp
  # TYPE rundeck_project_start_timestamp gauge
  rundeck_project_start_timestamp{execution_id="48123",execution_type="scheduled",job_group="",job_id="fdd65faa-31f7-46d5-be3d-6f4904720231",job_name="Success after 15s",project_name="OtherTest",user="admin"} 1.636200048005e+012
  # HELP rundeck_project_execution_duration_seconds Rundeck Project OtherTest Execution Duration
  # TYPE rundeck_project_execution_duration_seconds gauge
  rundeck_project_execution_duration_seconds{execution_id="48123",execution_type="scheduled",job_group="",job_id="fdd65faa-31f7-46d5-be3d-6f4904720231",job_name="Success after 15s",project_name="OtherTest",user="admin"} 15274.0
  # HELP rundeck_project_execution_status Rundeck Project OtherTest Execution Status
  # TYPE rundeck_project_execution_status gauge
  rundeck_project_execution_status{execution_id="48123",execution_type="scheduled",job_group="",job_id="fdd65faa-31f7-46d5-be3d-6f4904720231",job_name="Success after 15s",project_name="OtherTest",status="succeeded",user="admin"} 1.0
  rundeck_project_execution_status{execution_id="48123",execution_type="scheduled",job_group="",job_id="fdd65faa-31f7-46d5-be3d-6f4904720231",job_name="Success after 15s",project_name="OtherTest",status="running",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="48123",execution_type="scheduled",job_group="",job_id="fdd65faa-31f7-46d5-be3d-6f4904720231",job_name="Success after 15s",project_name="OtherTest",status="failed",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="48123",execution_type="scheduled",job_group="",job_id="fdd65faa-31f7-46d5-be3d-6f4904720231",job_name="Success after 15s",project_name="OtherTest",status="aborted",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="48123",execution_type="scheduled",job_group="",job_id="fdd65faa-31f7-46d5-be3d-6f4904720231",job_name="Success after 15s",project_name="OtherTest",status="unknown",user="admin"} 0.0
  # HELP rundeck_project_start_timestamp Rundeck Project OtherTest Start Timestamp
  # TYPE rundeck_project_start_timestamp gauge
  rundeck_project_start_timestamp{execution_id="48111",execution_type="scheduled",job_group="",job_id="1fb00970-dc94-4260-af49-812397d1b0af",job_name="Fail after 30s",project_name="OtherTest",user="admin"} 1.636200031008e+012
  # HELP rundeck_project_execution_duration_seconds Rundeck Project OtherTest Execution Duration
  # TYPE rundeck_project_execution_duration_seconds gauge
  rundeck_project_execution_duration_seconds{execution_id="48111",execution_type="scheduled",job_group="",job_id="1fb00970-dc94-4260-af49-812397d1b0af",job_name="Fail after 30s",project_name="OtherTest",user="admin"} 30023.0
  # HELP rundeck_project_execution_status Rundeck Project OtherTest Execution Status
  # TYPE rundeck_project_execution_status gauge
  rundeck_project_execution_status{execution_id="48111",execution_type="scheduled",job_group="",job_id="1fb00970-dc94-4260-af49-812397d1b0af",job_name="Fail after 30s",project_name="OtherTest",status="succeeded",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="48111",execution_type="scheduled",job_group="",job_id="1fb00970-dc94-4260-af49-812397d1b0af",job_name="Fail after 30s",project_name="OtherTest",status="running",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="48111",execution_type="scheduled",job_group="",job_id="1fb00970-dc94-4260-af49-812397d1b0af",job_name="Fail after 30s",project_name="OtherTest",status="failed",user="admin"} 1.0
  rundeck_project_execution_status{execution_id="48111",execution_type="scheduled",job_group="",job_id="1fb00970-dc94-4260-af49-812397d1b0af",job_name="Fail after 30s",project_name="OtherTest",status="aborted",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="48111",execution_type="scheduled",job_group="",job_id="1fb00970-dc94-4260-af49-812397d1b0af",job_name="Fail after 30s",project_name="OtherTest",status="unknown",user="admin"} 0.0
  # HELP rundeck_project_start_timestamp Rundeck Project OtherTest Start Timestamp
  # TYPE rundeck_project_start_timestamp gauge
  rundeck_project_start_timestamp{execution_id="48125",execution_type="scheduled",job_group="",job_id="4c73d97f-4f2c-4f5f-bb73-cc02a0166bce",job_name="Success after 5s",project_name="OtherTest",user="admin"} 1.636200054006e+012
  # HELP rundeck_project_execution_duration_seconds Rundeck Project OtherTest Execution Duration
  # TYPE rundeck_project_execution_duration_seconds gauge
  rundeck_project_execution_duration_seconds{execution_id="48125",execution_type="scheduled",job_group="",job_id="4c73d97f-4f2c-4f5f-bb73-cc02a0166bce",job_name="Success after 5s",project_name="OtherTest",user="admin"} 5287.0
  # HELP rundeck_project_execution_status Rundeck Project OtherTest Execution Status
  # TYPE rundeck_project_execution_status gauge
  rundeck_project_execution_status{execution_id="48125",execution_type="scheduled",job_group="",job_id="4c73d97f-4f2c-4f5f-bb73-cc02a0166bce",job_name="Success after 5s",project_name="OtherTest",status="succeeded",user="admin"} 1.0
  rundeck_project_execution_status{execution_id="48125",execution_type="scheduled",job_group="",job_id="4c73d97f-4f2c-4f5f-bb73-cc02a0166bce",job_name="Success after 5s",project_name="OtherTest",status="running",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="48125",execution_type="scheduled",job_group="",job_id="4c73d97f-4f2c-4f5f-bb73-cc02a0166bce",job_name="Success after 5s",project_name="OtherTest",status="failed",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="48125",execution_type="scheduled",job_group="",job_id="4c73d97f-4f2c-4f5f-bb73-cc02a0166bce",job_name="Success after 5s",project_name="OtherTest",status="aborted",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="48125",execution_type="scheduled",job_group="",job_id="4c73d97f-4f2c-4f5f-bb73-cc02a0166bce",job_name="Success after 5s",project_name="OtherTest",status="unknown",user="admin"} 0.0
  # HELP rundeck_project_start_timestamp Rundeck Project Test Start Timestamp
  # TYPE rundeck_project_start_timestamp gauge
  rundeck_project_start_timestamp{execution_id="48155",execution_type="scheduled",job_group="",job_id="1d225545-8e09-4fb5-aa3a-b11b176d7b40",job_name="Fail after 5s",project_name="Test",user="admin"} 1.636200222004e+012
  # HELP rundeck_project_execution_duration_seconds Rundeck Project Test Execution Duration
  # TYPE rundeck_project_execution_duration_seconds gauge
  rundeck_project_execution_duration_seconds{execution_id="48155",execution_type="scheduled",job_group="",job_id="1d225545-8e09-4fb5-aa3a-b11b176d7b40",job_name="Fail after 5s",project_name="Test",user="admin"} -1636200222004.0
  # HELP rundeck_project_execution_status Rundeck Project Test Execution Status
  # TYPE rundeck_project_execution_status gauge
  rundeck_project_execution_status{execution_id="48155",execution_type="scheduled",job_group="",job_id="1d225545-8e09-4fb5-aa3a-b11b176d7b40",job_name="Fail after 5s",project_name="Test",status="succeeded",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="48155",execution_type="scheduled",job_group="",job_id="1d225545-8e09-4fb5-aa3a-b11b176d7b40",job_name="Fail after 5s",project_name="Test",status="running",user="admin"} 1.0
  rundeck_project_execution_status{execution_id="48155",execution_type="scheduled",job_group="",job_id="1d225545-8e09-4fb5-aa3a-b11b176d7b40",job_name="Fail after 5s",project_name="Test",status="failed",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="48155",execution_type="scheduled",job_group="",job_id="1d225545-8e09-4fb5-aa3a-b11b176d7b40",job_name="Fail after 5s",project_name="Test",status="aborted",user="admin"} 0.0
  rundeck_project_execution_status{execution_id="48155",execution_type="scheduled",job_group="",job_id="1d225545-8e09-4fb5-aa3a-b11b176d7b40",job_name="Fail after 5s",project_name="Test",status="unknown",user="admin"} 0.0
  ....
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

## Changelog
`2.4.3`:
* Fix issue #27 rundeck_scheduler_quartz_scheduledJobs not showing up
* Add rundeck.username and RUNDECK_PASSWORD env support for Rundeck API versions older than 24

`2.4.2`:
* Add hub.docker.com image build and publish
* Add .gitkeep file
* Update Version and api version unsupported message

`2.4.1`:
* Add docker-compose example

`2.4.0`:
* Add Grafana dashboard examples
* Add execution_type and user to rundeck_project_execution_status metrics

`2.3.2`:
* Fix -h/--help description about required RUNDECK_TOKEN env var
* Add pip requirements.txt file
* Update .gitignore
* Update Dockefile to use requirements.txt
* Update Makefile to get VERSION from rundeck_exporter.py

`2.3.1`:
* PR #19: Add job_group label to job metrics

`2.3.0`:
* Fix issue #16 - Added options --rundeck.cpu.stats, --rundeck.memory.stats and --version

`2.2.6`:
* Fix issue #14 - Fixed the info about running status

`2.2.5`:
* Fix issue #13 - Added new label execution_id to rundeck_project_execution_status metrics

`2.2.4`:
* Fix issue Regarding execution status #11 - Modified GaugeMetricFamily location in the function get_project_executions

`2.2.3`:
* Fix issue invalid API request #10 - Added warning message for API version < 25

`2.2.2`:
* Fix GaugeMetricFamily definition location on method get_project_executions to correctly shows the HELP/TYPE

`2.2.1`:
* Fix exception messages on failed Rundeck api requests

`v2.2.0`:
* Fix issue Last Run #5 - Merged @h4wkmoon patch that adds rundeck_project_start_timestamp metric

`v2.1.0`:
* Fix issue Long Running Jobs #2 - Add metric rundeck_project_execution_duration_seconds
* Fix issue Project executions metrics not show all jobs info #4
* Add pull request fix order labels and values the same way in execution metrics #3

`v2.0.0`:
* Fix json response validation
* Add param --rundeck.projects.executions.cache and env RUNDECK_PROJECTS_EXECUTIONS_CACHE
* Add counter metrics rundeck_services_[services,controllers,api,web]_total
* Remove all gauge metrics rundeck_[services,controllers,api,web]...{type="..."}
* Remove metrics rundeck_system_stats_[cpu,memory,uptime_duration]...
* Remove param --rundeck.token. Need RUNDECK_TOKEN env now.
* Remove param --rundeck.projects.executions.limit
* Remove rundeck_node label from all metrics
* Change rundeck_project_executions_info metrics to rundeck_project_status{job_id=...,job_name=...,project_name=...,status=....}

`v1.2.0`:
* Add new params:
  * --debug: Enable debug mode
  * --rundeck.projects.executions: Get projects executions metrics
  * --rundeck.projects.filter: Get executions only from listed projects (delimiter = space)
  * --rundeck.projects.executions.limit: Limit project executions metrics query. Default: 20
  * --rundeck.cached.requests.ttl: Rundeck cached requests (by now, only for rundeck.projects.executions) expiration time. Default: 120
* Add code improvements
* Add cachetools to pip install on Dockerfile
* Add logging module to replace print calls
* Add better error handling
* Change args location, now located at class RundeckMetricsCollector

`v1.1.1`:
* Fix metrics collection bug

`v1.1.0`:
* Support for environment variables
* Better excpetions treatment

`v1.0.0`:
* Initial release
