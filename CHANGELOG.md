# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/phsmith/rundeck_exporter/compare/v3.0.0...HEAD)

## [2.8.5](https://github.com/phsmith/rundeck_exporter/compare/v2.8.4...v2.8.5) - 2025-08-07

### Fixed

- Fix Dockerfile by @gilankpam in [#111](https://github.com/phsmith/rundeck_exporter/pull/111)
- Fix sporadic python errors by @jrelax in [#113](https://github.com/phsmith/rundeck_exporter/pull/113)

## [2.8.4](https://github.com/phsmith/rundeck_exporter/compare/v2.8.3...v2.8.4) - 2025-01-13

### Changed

- Bump chart version (`0.3.1`)

### Fixed

- Helm chart error when using `serviceMonitor.name` (formatting error)
- Remove default `RUNDECK_TOKEN` env variable (default value overrules value from secret if set)
- Issue [#108](https://github.com/phsmith/rundeck_exporter/issues/108), fix Prometheus duplicate metrics error report when `rundeck.projects.executions.cache` option is enabled.

## [2.8.3](https://github.com/phsmith/rundeck_exporter/compare/v2.8.2...v2.8.3) - 2024-10-16

### Fixed

- Issue [#103](https://github.com/phsmith/rundeck_exporter/issues/103), fix boolean env vars broken in Python > 3.12.

## [2.8.2](https://github.com/phsmith/rundeck_exporter/compare/v2.8.1...v2.8.2) - 2024-09-11

### Fixed

- Issue [#101](https://github.com/phsmith/rundeck_exporter/issues/101), fix broken validation of boolean environment variables.

## [2.8.1](https://github.com/phsmith/rundeck_exporter/compare/v2.8.0...v2.8.1) - 2024-09-01

### Fixed

- Return the accidentally removed `no_checks_in_passive_mode` condition.

## [2.8.0](https://github.com/phsmith/rundeck_exporter/compare/v2.7.1...v2.8.0) - 2024-08-31

### Added

- Issue [#97](https://github.com/phsmith/rundeck_exporter/issues/97), new rundeck_execution_mode_<active/passive> metrics.

### Changed

- Update Docker Compose example files.

## Fixed

- Issue [#95](https://github.com/phsmith/rundeck_exporter/issues/95), improved and fixed the exporter helm chart.
- Issue [#98](https://github.com/phsmith/rundeck_exporter/issues/98), fixed exception errors when the user does not have the required permissions.

## [2.7.1](https://github.com/phsmith/rundeck_exporter/compare/v2.7.0...v2.7.1) - 2024-05-30

### Added

- Fix security issue by avoiding running container as root in Dockerfile by @nataliagranato in [https://github.com/phsmith/rundeck_exporter/pull/92](https://github.com/phsmith/rundeck_exporter/pull/92)
- Improve docker build and publish actions workflow by @phsmith in [https://github.com/phsmith/rundeck_exporter/pull/93](https://github.com/phsmith/rundeck_exporter/pull/93)

## [2.7.0](https://github.com/phsmith/rundeck_exporter/compare/v2.6.5...v2.7.0) - 2024-04-20

### Added

- Added the following new arguments:
  - `--rundeck.projects.nodes.info` - If passed, display Rundeck projects nodes info metrics, currently only the `rundeck_project_nodes_total` metric is available.
    - Requests for this check are cached as it can cause high CPU load depending on the number of projects.
    
  - `--threadpool_max_workers` - The maximum number of workers in the threadpool to run rundeck_exporter asynchronous checks.
    - Defaults to `(number of CPUs) + 4`, which may be too much on a server running other services.
    
  - `--rundeck.requests.timeout` - The maximum number of seconds that requests to the Rundeck API should timeout.
    - Defaults to 30.
    
  

### Changed

- Changed the functions `request_data_from` and `cached_request_data_from` to `request` and `cached_request`, respectively.

### Fixed

- Issue [#89](https://github.com/phsmith/rundeck_exporter/issues/89), correctly started the `project_executions_total` variable and also fixed the metric return.

## [2.6.5](https://github.com/phsmith/rundeck_exporter/compare/v2.6.4...v2.6.5) - 2024-03-11

### Added

- Issue [#85](https://github.com/phsmith/rundeck_exporter/issues/85), added new metric `rundeck_project_nodes_total`.

## [2.6.4](https://github.com/phsmith/rundeck_exporter/compare/v2.6.3...v2.6.4) - 2024-03-05

### Added

- Issue [#83](https://github.com/phsmith/rundeck_exporter/issues/83), added new `--no_checks_in_passive_mode` argument and `RUNDECK_EXPORTER_NO_CHECKS_IN_PASSIVE_MODE=<False|True>` env var introduced to keep the rundeck_exporter idle while the Rundeck host is in `passive` execution mode.

## [2.6.3](https://github.com/phsmith/rundeck_exporter/compare/v2.6.2...v2.6.3) - 2023-11-10

### Added

- Added Helm Chart by @nataliagranato in [https://github.com/phsmith/rundeck_exporter/pull/76](https://github.com/phsmith/rundeck_exporter/pull/76)

### Fixed

- Issue [#77](https://github.com/phsmith/rundeck_exporter/issues/77), systemd service doesn't work according to docs.

### Removed

- Remove VERSION file and keep version in the app.

## [2.6.2](https://github.com/phsmith/rundeck_exporter/compare/v2.6.1...v2.6.2) - 2023-09-01

### Fixed

- Issue [#73](https://github.com/phsmith/rundeck_exporter/issues/73), fix VERSION file path.
- VERSION not found in docker image

## [2.6.1](https://github.com/phsmith/rundeck_exporter/compare/v2.6.0...v2.6.1) - 2023-06-01

### Fixed

- [PR#70](https://github.com/phsmith/rundeck_exporter/pull/70) Removed `recentFilter` query string from `/executions/running` endpoint
- [PR#71](https://github.com/phsmith/rundeck_exporter/pull/71) Bumped requests library version to [latest stable version](https://github.com/psf/requests/releases/tag/v2.31.0) that mitigates [CVE-2023-32681](https://nvd.nist.gov/vuln/detail/CVE-2023-32681)

## [2.6.0](https://github.com/phsmith/rundeck_exporter/compare/v2.5.2...v2.6.0) - 2023-05-30

### Added

- Issue [#68](https://github.com/phsmith/rundeck_exporter/issues/68), added new argument `rundeck.projects.executions.filter`

## [2.5.2](https://github.com/phsmith/rundeck_exporter/compare/v2.5.1...v2.5.2) - 2023-05-02

### Changed

- Update Dockerfile and Makefile to support the new VERSION file

### Fixed

- Fixed rundeck_project_execution_duration_seconds metric return values from milliseconds to seconds

## [2.5.1](https://github.com/phsmith/rundeck_exporter/compare/v2.5.0...v2.5.1) - 2023-05-02

### Added

- Added VERSION file

### Fixed

- Fixed issue [#65](https://github.com/phsmith/rundeck_exporter/issues/65), rundeck_project_execution_duration_seconds metric reporting wrong values. Instead of using the job `averageDuration` attribute, now the value is calculated based on the `start time` and `end time`

## [2.5.0](https://github.com/phsmith/rundeck_exporter/compare/v2.4.14...v2.5.0) - 2022-09-29

### Added

- Added new metric `rundeck_project_executions_total`

### Fixed

- Fixed issue [#59](https://github.com/phsmith/rundeck_exporter/issues/59), unable to pass the RUNDECK_PROJECTS_FILTER environment variables

## [2.4.14](https://github.com/phsmith/rundeck_exporter/compare/v2.4.13...v2.4.14) - 2022-07-21

### Added

- rundeck.projects.executions.limit argument

### Fixed

- Inaccurate projects executions results, Details on issue #56

## [2.4.13](https://github.com/phsmith/rundeck_exporter/compare/v2.4.12...v2.4.13) - 2022-07-19

### Added

- Increased project executions max limit results to 250. Details on issue [#56](https://github.com/phsmith/rundeck_exporter/issues/56)

## [2.4.12](https://github.com/phsmith/rundeck_exporter/compare/v2.4.11...v2.4.12) - 2022-07-04

### Fixed

- Fixed issue [#55](https://github.com/phsmith/rundeck_exporter/issues/55), support for Python 3.6

## [2.4.11](https://github.com/phsmith/rundeck_exporter/compare/v2.4.10...v2.4.11) - 2022-06-11

### Added

- Moved changelogs from README.md to CHANGELOG.md
- Added changelogs version compare links

### Fixed

- Update exporter version

## [2.4.10](https://github.com/phsmith/rundeck_exporter/compare/v2.4.9...v2.4.10) - 2022-06-07

### Fixed

- Cast api_version to an integer by @broferek in [https://github.com/phsmith/rundeck_exporter/pull/51](https://github.com/phsmith/rundeck_exporter/pull/51)

## [2.4.9](https://github.com/phsmith/rundeck_exporter/compare/v2.4.8...v2.4.9) - 2022-05-09

### Fixed

- Fixed version
- Fixed issue [#42](https://github.com/phsmith/rundeck_exporter/issues/42), avoid duplicating metric definitions by @WilsonSunBritten in [https://github.com/phsmith/rundeck_exporter/pull/46](https://github.com/phsmith/rundeck_exporter/pull/46)

## [2.4.8](https://github.com/phsmith/rundeck_exporter/compare/v2.4.7...v2.4.8) - 2022-05-09

### Fixed

- Fixed issue [#42](https://github.com/phsmith/rundeck_exporter/issues/42), avoid duplicating metric definitions by @WilsonSunBritten in [https://github.com/phsmith/rundeck_exporter/pull/43](https://github.com/phsmith/rundeck_exporter/pull/43)

## [2.4.7](https://github.com/phsmith/rundeck_exporter/compare/v2.4.6...v2.4.7) - 2022-04-20

### Changed

- Changed the job_execution_duration calc to get info from job attribute `averageDuration`

### Fixed

- Fixed issue [#40](https://github.com/phsmith/rundeck_exporter/issues/40), negative job_execution_duration value

## [2.4.6](https://github.com/phsmith/rundeck_exporter/compare/v2.4.5...v2.4.6) - 2022-03-05

### Added

- Added `instance_address` label in metrics

### Removed

- Removed `node` label from metrics

### Fixed

- Fixed issue [#34](https://github.com/phsmith/rundeck_exporter/issues/34) Put RUNDECK_URL into the label instance

## [2.4.5](https://github.com/phsmith/rundeck_exporter/compare/v2.4.4...v2.4.5) - 2022-03-03

### Added

- Added `node` label in metrics

### Fixed

- Fixed issue [#34](https://github.com/phsmith/rundeck_exporter/issues/34) Put RUNDECK_URL into the label instance

## [2.4.4](https://github.com/phsmith/rundeck_exporter/compare/v2.4.3...v2.4.4) - 2022-02-25

### Removed

- Removed the Rundeck token requiment if username and password options are used

## [2.4.3](https://github.com/phsmith/rundeck_exporter/compare/v2.4.2...v2.4.3) - 2022-02-24

### Added

- Added rundeck.username and RUNDECK_PASSWORD env support for Rundeck API versions older than 24

### Fixed

- Fixed issue [#27](https://github.com/phsmith/rundeck_exporter/issues/27) rundeck_scheduler_quartz_scheduledJobs not showing up

## [2.4.2](https://github.com/phsmith/rundeck_exporter/compare/v2.4.1...v2.4.2) - 2022-02-22

### Added

- Added hub.docker.com image build and publish
- Added .gitkeep file

### Changed

- Update Version and api version unsupported message

## [2.4.1](https://github.com/phsmith/rundeck_exporter/compare/v2.4.0...v2.4.1) - 2021-12-27

### Added

- Added docker-compose example

## [2.4.0](https://github.com/phsmith/rundeck_exporter/compare/v2.3.2...v2.4.0) - 202-11-06

### Added

- Added Grafana dashboard examples
- Added execution_type and user to rundeck_project_execution_status metrics

## [2.3.2](https://github.com/phsmith/rundeck_exporter/compare/v2.3.1...v2.3.2) - 2021-09-24

### Added

- Added pip requirements.txt file

### Changed

- Update .gitignore
- Update Dockefile to use requirements.txt
- Update Makefile to get VERSION from rundeck_exporter.py

### Fixed

- Fixed -h/--help description about required RUNDECK_TOKEN env var

## [2.3.1](https://github.com/phsmith/rundeck_exporter/compare/v2.3.0...v2.3.1) - 2021-07-28

### Added

- PR #19: Added job_group label to job metrics

## [2.3.0](https://github.com/phsmith/rundeck_exporter/compare/v2.2.6...v2.3.0) - 2021-04-15

### Fixed

- Fixed issue [#16](https://github.com/phsmith/rundeck_exporter/issues/16) - Added options --rundeck.cpu.stats, --rundeck.memory.stats and --version

## [2.2.6](https://github.com/phsmith/rundeck_exporter/compare/v2.2.5...v2.2.6) - 2021-03-31

### Fixed

- Fixed issue [#14](https://github.com/phsmith/rundeck_exporter/issues/14) - Fixed the info about running status

## [2.2.5](https://github.com/phsmith/rundeck_exporter/compare/v2.2.4...v2.2.5) - 2021-03-22

### Fixed

- Fixed issue [#13](https://github.com/phsmith/rundeck_exporter/issues/13) - Added new label execution_id to rundeck_project_execution_status metrics

## [2.2.4](https://github.com/phsmith/rundeck_exporter/compare/v2.2.3...v2.2.4) - 2021-03-02

### Fixed

- Fixed issue Regarding execution status [#11](https://github.com/phsmith/rundeck_exporter/issues/11) - Modified GaugeMetricFamily location in the function get_project_executions

## [2.2.3](https://github.com/phsmith/rundeck_exporter/compare/v2.2.2...v2.2.3) - 2021-02-26

### Fixed

- Fixed issue invalid API request [#10](https://github.com/phsmith/rundeck_exporter/issues/10) - Added warning message for API version < 25

## [2.2.2](https://github.com/phsmith/rundeck_exporter/compare/v2.2.1...v2.2.2) - 2021-01-05

### Fixed

- Fixed GaugeMetricFamily definition location on method get_project_executions to correctly shows the HELP/TYPE

## [2.2.1](https://github.com/phsmith/rundeck_exporter/compare/v2.2.0...v2.2.1) - 2020-12-15

### Fixed

- Fixed exception messages on failed Rundeck api requests

## [2.2.0](https://github.com/phsmith/rundeck_exporter/compare/v2.1.0...v2.2.0) - 2020-11-28

### Fixed

- Fixed issue Last Run [#5](https://github.com/phsmith/rundeck_exporter/issues/5) - Merged @h4wkmoon patch that adds rundeck_project_start_timestamp metric

## [2.1.0](https://github.com/phsmith/rundeck_exporter/compare/v2.0.0...v2.1.0) - 2020-11-04

### Added

- Added pull request Fixed order labels and values the same way in execution metrics [#3](https://github.com/phsmith/rundeck_exporter/issues/3)

### Fixed

- Fixed issue [#2](https://github.com/phsmith/rundeck_exporter/issues/2), Long Running Jobs. Added metric rundeck_project_execution_duration_seconds
- Fixed issue [#4](https://github.com/phsmith/rundeck_exporter/issues/4), Project executions metrics not show all jobs info

## [2.0.0](https://github.com/phsmith/rundeck_exporter/compare/v1.2.0...v2.0.0) - 2020-08-12

### Added

- Added argument `--rundeck.projects.executions.cache` and  `RUNDECK_PROJECTS_EXECUTIONS_CACHE` env var
- Added counter metrics rundeck_services_[services,controllers,api,web]_total

### Changed

- Changed rundeck_project_executions_info metrics to rundeck_project_status{job_id=...,job_name=...,project_name=...,status=....}

### Removed

- Removed all gauge metrics rundeck_[services,controllers,api,web]...{type="..."}
- Removed metrics rundeck_system_stats_[cpu,memory,uptime_duration]...
- Removed argument `--rundeck.token`. Need `RUNDECK_TOKEN` env now.
- Removed argument `--rundeck.projects.executions.limit`
- Removed rundeck_node label from all metrics

### Fixed

- Fixed json response validation

## [1.2.0](https://github.com/phsmith/rundeck_exporter/compare/v1.1.1...v1.2.0) - 2020-08-06

### Added

- Added new argument:
  - `--debug`: Enable debug mode
  - `--rundeck.projects.executions`: Get projects executions metrics
  - `--rundeck.projects.filter`: Get executions only from listed projects (delimiter = space)
  - `--rundeck.projects.executions.limit`: Limit project executions metrics query. Default: 20
  - `--rundeck.cached.requests.ttl`: Rundeck cached requests (by now, only for rundeck.projects.executions) expiration time. Default: 120
  
- Added code improvements
- Added cachetools to pip install on Dockerfile
- Added logging module to replace print calls
- Added better error handling

### Changed

- Changed args location, now located at class RundeckMetricsCollector

## [1.1.1](https://github.com/phsmith/rundeck_exporter/compare/v1.1.0...v1.1.1) - 2019-09-24

### Fixed

- Fixed metrics collection bug

## [1.1.0](https://github.com/phsmith/rundeck_exporter/compare/v1.0.0...v1.1.0) - 2019-07-31

### Added

- Added support for environment variables

### Changed

- Better excpetions treatment

## [1.0.0](https://github.com/phsmith/rundeck_exporter/releases/tag/v1.0.0) - 2019-07-23

### Added

- Initial release

## [v3.0.0](https://github.com/phsmith/rundeck_exporter/compare/v2.8.5...v3.0.0) - 2025-08-27

### What's Changed

- Added pr-checks, relase and update-changelog gh actions
- Added docker-compose-ci.yml
- Added `UV` as the default package and project manager
- Added test/test_rundeck_exporter_metrics.py
- Added src/rundeck_exporter module
  - `args.py`: module responsible for the CLI arguments definition
  - `cli.py`: module that initializes the rundeck_exporter command line interface.
  - `constants.py`: module that stores the app constants.
  - `metrics_collector.py`: module that handles all the Rundeck metrics collection.
  - `utils.py`: module containing utilities and middlewares used by the  modules.
  
- Updated docker-compose examples and configs
- Updated README.md
- Removed rundeck_exporter.py. The code was refactored in the `src/rundeck_exporter` module.

**Full Changelog**: https://github.com/phsmith/rundeck_exporter/compare/v2.8.5...v3.0.0
