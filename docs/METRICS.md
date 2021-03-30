## Rundeck Metrics Documentation

## rundeck_system_info

Basic information about Rundeck like api version, build version, base directory installation, etc.

```
# HELP rundeck_system_info Rundeck system info
# TYPE rundeck_system_info gauge
rundeck_system_info{apiversion="35",base="/home/rundeck",build="3.2.8-20200608",buildGit="v3.2.8-20200608-0-g7e632f5",node="rundeck-host",serverUUID="868e9175-b09f-4732-ac4a-71b62545d79b",version="3.2.8-20200608"} 1.0
```

## rundeck_system_stats_uptime_since

Startup time as time since the unix epoch

```
# HELP rundeck_system_stats_uptime_since Rundeck system stats
# TYPE rundeck_system_stats_uptime_since gauge
rundeck_system_stats_uptime_since 1.617092384808e+012
```

## rundeck_system_stats_scheduler_running

Number of running jobs in the scheduler

```
# HELP rundeck_system_stats_scheduler_running Rundeck system stats
# TYPE rundeck_system_stats_scheduler_running gauge
rundeck_system_stats_scheduler_running 0.0
```

## rundeck_system_stats_scheduler_threadPoolSize

Size of the scheduler threadPool: maximum number of concurrent Rundeck executions

```
# HELP rundeck_system_stats_scheduler_threadPoolSize Rundeck system stats
# TYPE rundeck_system_stats_scheduler_threadPoolSize gauge
rundeck_system_stats_scheduler_threadPoolSize 200.0
```

## rundeck_system_stats_threads_active

Number of active Threads in the JVM

```
# HELP rundeck_system_stats_threads_active Rundeck system stats
# TYPE rundeck_system_stats_threads_active gauge
rundeck_system_stats_threads_active 232.0
```

## rundeck_dataSource_connection_pingTime

No references for documentation found.

```
# HELP rundeck_dataSource_connection_pingTime Rundeck gauges metrics
# TYPE rundeck_dataSource_connection_pingTime gauge
rundeck_dataSource_connection_pingTime 0.0
```

## rundeck_scheduler_quartz_runningExecutions

Number executions currently running

```
# HELP rundeck_scheduler_quartz_runningExecutions Rundeck gauges metrics
# TYPE rundeck_scheduler_quartz_runningExecutions gauge
rundeck_scheduler_quartz_runningExecutions 0.0
```

## rundeck_scheduler_quartz_scheduledJobs

Number of scheduled jobs

```
# HELP rundeck_scheduler_quartz_scheduledJobs Rundeck counters metrics
# TYPE rundeck_scheduler_quartz_scheduledJobs gauge
rundeck_scheduler_quartz_scheduledJobs 0.0
```

## rundeck_api_requests_requestTimer_total

Number of requests per second on Rundeck API

```
# HELP rundeck_api_requests_requestTimer_total Rundeck timers metrics
# TYPE rundeck_api_requests_requestTimer_total counter
rundeck_api_requests_requestTimer_total 395.0
```

## rundeck_web_requests_requestTimer_total

Number of requests per second on Rundeck web page

```
# HELP rundeck_web_requests_requestTimer_total Rundeck timers metrics
# TYPE rundeck_web_requests_requestTimer_total counter
rundeck_web_requests_requestTimer_total 1498.0
```

## rundeck_services_*_sourceCache_evictionCount_total
Cache eviction of the services (free memory of the old, unused data in the cache)

```
# HELP rundeck_services_AuthorizationService_sourceCache_evictionCount_total Rundeck gauges metrics
# TYPE rundeck_services_AuthorizationService_sourceCache_evictionCount_total counter
rundeck_services_AuthorizationService_sourceCache_evictionCount_total 0.0
```

## rundeck_services_*_sourceCache_hitCount_total

Number of successfull hits on services cache

```
# HELP rundeck_services_AuthorizationService_sourceCache_hitCount_total Rundeck gauges metrics
# TYPE rundeck_services_AuthorizationService_sourceCache_hitCount_total counter
rundeck_services_AuthorizationService_sourceCache_hitCount_total 31995.0
```
## rundeck_services_*_sourceCache_loadExceptionCount_total

No references for documentation found.

```
# HELP rundeck_services_AuthorizationService_sourceCache_loadExceptionCount_total Rundeck gauges metrics
# TYPE rundeck_services_AuthorizationService_sourceCache_loadExceptionCount_total counter
rundeck_services_AuthorizationService_sourceCache_loadExceptionCount_total 0.0
```

## rundeck_services_*_sourceCache_missCount_total

Number of missed cache hits on services

```
# HELP rundeck_services_AuthorizationService_sourceCache_missCount_total Rundeck gauges metrics
# TYPE rundeck_services_AuthorizationService_sourceCache_missCount_total counter
rundeck_services_AuthorizationService_sourceCache_missCount_total 81.0
```

## rundeck_services_AuthorizationService_*

No references for documentation found.

```
# HELP rundeck_services_AuthorizationService_systemAuthorization_evaluateMeter_total Rundeck meters metrics
# TYPE rundeck_services_AuthorizationService_systemAuthorization_evaluateMeter_total counter
rundeck_services_AuthorizationService_systemAuthorization_evaluateMeter_total 762.0
# HELP rundeck_services_AuthorizationService_systemAuthorization_evaluateSetMeter_total Rundeck meters metrics
# TYPE rundeck_services_AuthorizationService_systemAuthorization_evaluateSetMeter_total counter
rundeck_services_AuthorizationService_systemAuthorization_evaluateSetMeter_total 28.0
```

## rundeck_services_ExecutionService_*

No references for documentation found.

```
# HELP rundeck_services_ExecutionService_executionFailureMeter_total Rundeck meters metrics
# TYPE rundeck_services_ExecutionService_executionFailureMeter_total counter
rundeck_services_ExecutionService_executionFailureMeter_total 1.0
# HELP rundeck_services_ExecutionService_executionJobStartMeter_total Rundeck meters metrics
# TYPE rundeck_services_ExecutionService_executionJobStartMeter_total counter
rundeck_services_ExecutionService_executionJobStartMeter_total 5.0
# HELP rundeck_services_ExecutionService_executionStartMeter_total Rundeck meters metrics
# TYPE rundeck_services_ExecutionService_executionStartMeter_total counter
rundeck_services_ExecutionService_executionStartMeter_total 5.0
# HELP rundeck_services_ExecutionService_executionSuccessMeter_total Rundeck meters metrics
# TYPE rundeck_services_ExecutionService_executionSuccessMeter_total counter
rundeck_services_ExecutionService_executionSuccessMeter_total 4.0
```

## rundeck_services_FrameworkService_*

No references for documentation found.

```
# HELP rundeck_services_FrameworkService_authorizeApplicationResource_total Rundeck timers metrics
# TYPE rundeck_services_FrameworkService_authorizeApplicationResource_total counter
rundeck_services_FrameworkService_authorizeApplicationResource_total 339.0
# HELP rundeck_services_FrameworkService_authorizeProjectJobAll_total Rundeck timers metrics
# TYPE rundeck_services_FrameworkService_authorizeProjectJobAll_total counter
rundeck_services_FrameworkService_authorizeProjectJobAll_total 2.0
# HELP rundeck_services_FrameworkService_filterAuthorizedProjectExecutionsAll_total Rundeck timers metrics
# TYPE rundeck_services_FrameworkService_filterAuthorizedProjectExecutionsAll_total counter
rundeck_services_FrameworkService_filterAuthorizedProjectExecutionsAll_total 57.0
```

## rundeck_services_NodeService_*

No references for documentation found.

```
# HELP rundeck_services_NodeService_project_rundeck_project_total Rundeck timers metrics
# TYPE rundeck_services_NodeService_project_rundeck_project_total counter
rundeck_services_NodeService_project_rundeck_project_total 1.0
```

## rundeck_project_start_timestamp

Project job execution start time since unix epoch

```
# HELP rundeck_project_start_timestamp Rundeck Project rundeck_project Start Timestamp
# TYPE rundeck_project_start_timestamp gauge
rundeck_project_start_timestamp{execution_id="2016583",job_id="39156aa3-978d-43d3-a642-1fb217b5822f",job_name="rundeck_job",project_name="rundeck_project"} 1.617059245e+012
```

## rundeck_project_execution_duration_seconds

Project job execution duration in seconds

```
# HELP rundeck_project_execution_duration_seconds Rundeck Project rundeck_project Execution Duration
# TYPE rundeck_project_execution_duration_seconds gauge
rundeck_project_execution_duration_seconds{execution_id="2016583",job_id="39156aa3-978d-43d3-a642-1fb217b5822f",job_name="rundeck_job",project_name="rundeck_project"} 5000.0
```

## rundeck_project_execution_status

Project job execution status. Value is set to 1 on the current status.

```
# HELP rundeck_project_execution_status Rundeck Project rundeck_project Execution Status
# TYPE rundeck_project_execution_status gauge
rundeck_project_execution_status{execution_id="2016583",job_id="39156aa3-978d-43d3-a642-1fb217b5822f",job_name="rundeck_job",project_name="rundeck_project",status="succeeded"} 1.0
rundeck_project_execution_status{execution_id="2016583",job_id="39156aa3-978d-43d3-a642-1fb217b5822f",job_name="rundeck_job",project_name="rundeck_project",status="running"} 0.0
rundeck_project_execution_status{execution_id="2016583",job_id="39156aa3-978d-43d3-a642-1fb217b5822f",job_name="rundeck_job",project_name="rundeck_project",status="failed"} 0.0
rundeck_project_execution_status{execution_id="2016583",job_id="39156aa3-978d-43d3-a642-1fb217b5822f",job_name="rundeck_job",project_name="rundeck_project",status="aborted"} 0.0
rundeck_project_execution_status{execution_id="2016583",job_id="39156aa3-978d-43d3-a642-1fb217b5822f",job_name="rundeck_job",project_name="rundeck_project",status="unknown"} 0.0
```
