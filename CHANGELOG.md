# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [5.0.0](https://github.com/phsmith/rundeck_exporter/compare/v4.0.1...v5.0.0) (2026-06-15)


### ⚠ BREAKING CHANGES

* rundeck_project_executions_total renamed to rundeck_project_executions and type changed Counter→Gauge. Update dashboards, alerts, and recording rules referencing the old name.

### Features

* **#76:** add helm chart ([b726ba0](https://github.com/phsmith/rundeck_exporter/commit/b726ba07d0de43eedf06434f2ea837b20c41d4bf))
* Add Changelogs ([eea99d6](https://github.com/phsmith/rundeck_exporter/commit/eea99d61728e4dbbbb188ebd0acc9d2d071e4ace))
* Add changelogs version compare links ([12d48c1](https://github.com/phsmith/rundeck_exporter/commit/12d48c1027e34e46d6057d3a69d5ed4a905b4ca2))
* Add docker-compose example. Issue [#26](https://github.com/phsmith/rundeck_exporter/issues/26). ([f7ffcb0](https://github.com/phsmith/rundeck_exporter/commit/f7ffcb0b520bddaf36dc0839c510e86273e390cb))
* add job_options label to project_execution metrics ([64a7e60](https://github.com/phsmith/rundeck_exporter/commit/64a7e603259cadcecdfccf1ac2cec18ee2e73162))
* add new metric rundeck_project_executions_total ([4d10c54](https://github.com/phsmith/rundeck_exporter/commit/4d10c542e6c8b6c1ee0bdfd9517e6b184d5aefde))
* add new metric rundeck_project_nodes_total ([#86](https://github.com/phsmith/rundeck_exporter/issues/86)) ([a3bffa8](https://github.com/phsmith/rundeck_exporter/commit/a3bffa8995600b8ce922b8ebb682963dadced769))
* add rundeck-config.properties remcom template to docker-compose example ([015f783](https://github.com/phsmith/rundeck_exporter/commit/015f783ae62bfba15c73de0ea7bdc11603359ff0))
* bump exporter version ([d36cd33](https://github.com/phsmith/rundeck_exporter/commit/d36cd331cd36471186752b550326e986b9c65570))
* Issue  [#56](https://github.com/phsmith/rundeck_exporter/issues/56), increase project executions max limit results to 250 ([d48ea0c](https://github.com/phsmith/rundeck_exporter/commit/d48ea0c480eeaffdbb12e206532ceda2dccc90ea))
* Updatea .gitignore ([6485171](https://github.com/phsmith/rundeck_exporter/commit/6485171112239c3458c935a4ea99b3189c2b9d5a))


### Bug Fixes

* **#103:** boolean env vars broken in python &gt; 3.12 ([#104](https://github.com/phsmith/rundeck_exporter/issues/104)) ([4888ec3](https://github.com/phsmith/rundeck_exporter/commit/4888ec3b19e524d004d4ca22296a3177d755e282))
* **#108:** add timestamp to project executions metrics ([#109](https://github.com/phsmith/rundeck_exporter/issues/109)) ([49d7e05](https://github.com/phsmith/rundeck_exporter/commit/49d7e059af4e2c2bcd13f8fb0097ae92b1508797))
* **#65:** change job_execution_duration calc ([d696b0e](https://github.com/phsmith/rundeck_exporter/commit/d696b0ec46bf9cf59c2bdeca1e43f8c3048a03d0))
* **#73:** add absolute VERSION path. ([506af09](https://github.com/phsmith/rundeck_exporter/commit/506af098c5d7417aea32aba14328ac3131f95c69))
* **#77:** remove version file and keep version in the app ([c825a08](https://github.com/phsmith/rundeck_exporter/commit/c825a08513fcadfdcf5853afb0f535db3ddc3cfe))
* **#95:** improve rundeck-exporter helm charts ([#96](https://github.com/phsmith/rundeck_exporter/issues/96)) ([75dbdcf](https://github.com/phsmith/rundeck_exporter/commit/75dbdcfe33856cd021532a6d73a0bc9d559a50bd))
* 5 - Add Last Start time ([07b9c01](https://github.com/phsmith/rundeck_exporter/commit/07b9c01e9fe14cc21d459a02277db61d667760f6))
* Add node label in system_stats metrics ([#36](https://github.com/phsmith/rundeck_exporter/issues/36)) ([edf91cc](https://github.com/phsmith/rundeck_exporter/commit/edf91cc82578a074863e2cf3295a929d23262848))
* broken validation of boolean env vars ([#102](https://github.com/phsmith/rundeck_exporter/issues/102)) ([abac26c](https://github.com/phsmith/rundeck_exporter/commit/abac26ce2214ba630996360cb6395ff43d8e3e3b))
* change labels_value type hint from dict to list ([6e60bc2](https://github.com/phsmith/rundeck_exporter/commit/6e60bc23bceb0fd05688ff67e83be4ff4277e835))
* **ci:** add GITHUB_TOKEN env to Docker publish step ([acf83e7](https://github.com/phsmith/rundeck_exporter/commit/acf83e7c3360e6dbba63ec2e464595c4e4fd1b76))
* **ci:** add write permissions for contents and packages in release ([ed5a614](https://github.com/phsmith/rundeck_exporter/commit/ed5a61477325c5abb68791eb9eac8657f124f8dc))
* **ci:** fix release pipeline — draft releases, uv lock sync, and branch fix ([#134](https://github.com/phsmith/rundeck_exporter/issues/134)) ([8a02704](https://github.com/phsmith/rundeck_exporter/commit/8a027041ed8cd653c2b550aad7461a95c8555f63))
* **ci:** remove draft from release-please config to restore git tag creation ([1a52d54](https://github.com/phsmith/rundeck_exporter/commit/1a52d540a01df656f2b659341e60f153323732d2))
* **ci:** use build stage for dist artifact extraction in release ([09d1f4f](https://github.com/phsmith/rundeck_exporter/commit/09d1f4f0b0536c09162c313598d9ad35daacbef1))
* **ci:** use PAT for release-please and add workflow_dispatch to release ([#132](https://github.com/phsmith/rundeck_exporter/issues/132)) ([9e6310c](https://github.com/phsmith/rundeck_exporter/commit/9e6310c39ee1de26edebc008fd55eddc97543d2f))
* convert job_execution_duration from ms to s ([d3edbe1](https://github.com/phsmith/rundeck_exporter/commit/d3edbe15e8a5c1cbea3daa361efa27e8e719906f))
* helm chart syntax error and secrets handling ([#106](https://github.com/phsmith/rundeck_exporter/issues/106)) ([dbecf8b](https://github.com/phsmith/rundeck_exporter/commit/dbecf8b6e4fd131f23a835a1d4b0894b4371fba6))
* inaccurate projects executions results, issue [#56](https://github.com/phsmith/rundeck_exporter/issues/56) ([b9e4b9d](https://github.com/phsmith/rundeck_exporter/commit/b9e4b9d8283aef58150ace1f6fcb9a65c3810a23))
* Issue [#34](https://github.com/phsmith/rundeck_exporter/issues/34), added `instance_address` label in metrics ([#37](https://github.com/phsmith/rundeck_exporter/issues/37)) ([7e1c54d](https://github.com/phsmith/rundeck_exporter/commit/7e1c54d59211fffbd1e98ebb1f530ebbfdbc76c3))
* Issue [#40](https://github.com/phsmith/rundeck_exporter/issues/40), negative job_execution_duration value ([#41](https://github.com/phsmith/rundeck_exporter/issues/41)) ([2967b3a](https://github.com/phsmith/rundeck_exporter/commit/2967b3aa608dbd1427fefec0af913cf32a537244))
* Issue [#55](https://github.com/phsmith/rundeck_exporter/issues/55), add support for Python3.6 ([ce982bd](https://github.com/phsmith/rundeck_exporter/commit/ce982bd39479037118007736b5976c5eecb08569))
* issue [#59](https://github.com/phsmith/rundeck_exporter/issues/59), unable to pass the RUNDECK_PROJECTS_FILTER ([b7884d3](https://github.com/phsmith/rundeck_exporter/commit/b7884d37eef96951a5105d834228f2ecb8d02bf9))
* makefile docker-build ([7ccee27](https://github.com/phsmith/rundeck_exporter/commit/7ccee27694ebc50b0401daa7dc76c96b0e89c2b3))
* order labels and values the same way in execution metrics ([490af45](https://github.com/phsmith/rundeck_exporter/commit/490af45dc752b5c5f1b598bf5bfb296b44aa8eb7))
* order labels and values the same way in execution metrics ([7a3187b](https://github.com/phsmith/rundeck_exporter/commit/7a3187b83e38dbe044ea9de478c75c187ad6afa1))
* **release:** allow empty commit when version unchanged ([ddeb269](https://github.com/phsmith/rundeck_exporter/commit/ddeb269ee8b64e918b8c30f6394483d10e2d2cb5))
* Removed Changelogs ([ca1b2a0](https://github.com/phsmith/rundeck_exporter/commit/ca1b2a06f514d26c1b09744186de5dc21e5659c6))
* resolve type errors and add mypy type checking ([8c381c9](https://github.com/phsmith/rundeck_exporter/commit/8c381c9975472434b86cda35b76514eac0b8fcfa))
* rundeck_exporter exits if it is unable to reach the Rundeck host ([#120](https://github.com/phsmith/rundeck_exporter/issues/120)) ([24964cf](https://github.com/phsmith/rundeck_exporter/commit/24964cfebe6353c1436db183daffea45ea780238))
* tests ([6997216](https://github.com/phsmith/rundeck_exporter/commit/699721659e3384b71ffaaddb5ebc25e8591d4936))
* update Dockerfile and Makefile ([27445d6](https://github.com/phsmith/rundeck_exporter/commit/27445d648456883f0f5610d57ac53860672ac614))
* update test1.rdproject.jar ([dcdd42f](https://github.com/phsmith/rundeck_exporter/commit/dcdd42f08937d4df6f9b2956f3bdf4f699c256b0))
* Update version ([3bcf8fa](https://github.com/phsmith/rundeck_exporter/commit/3bcf8fa44cc3b85566fae203b384d6dea53178f3))
* update-changelog gh workflow ([b0476fa](https://github.com/phsmith/rundeck_exporter/commit/b0476fada3040a606595649b68c8e5ec3a9bdeef))
* **utils:** replace requests with httpx for thread-safe HTTP clients ([#127](https://github.com/phsmith/rundeck_exporter/issues/127)) ([554f326](https://github.com/phsmith/rundeck_exporter/commit/554f326695761bc03891dfe000e882de8809a3f3))
* Version and changelog update ([#48](https://github.com/phsmith/rundeck_exporter/issues/48)) ([1f7834a](https://github.com/phsmith/rundeck_exporter/commit/1f7834a93d5f4864743e019e0dd681ff3aa6abf8))
* version in docker-publish.yml ([eee5c49](https://github.com/phsmith/rundeck_exporter/commit/eee5c496103ef7e694f5bcad502877b2245268c3))
* VERSION not found in docker image ([4408355](https://github.com/phsmith/rundeck_exporter/commit/440835582152a3debb70c6248a7f8003fd1e3966))


### Documentation

* **#73:** update systemd example ([04448d1](https://github.com/phsmith/rundeck_exporter/commit/04448d1f6f8628304cd5915e16109d407a418532))
* **readme:** add Helm section, fix API version default, and improve Docker docs ([5ec815c](https://github.com/phsmith/rundeck_exporter/commit/5ec815cf5acd5b479d394ca73c6458e9d9fd1e47))
* update CHANGELOG ([37f50d3](https://github.com/phsmith/rundeck_exporter/commit/37f50d35c341e7fae3331c7a59b76a16ee3e06c0))
* update changelog.md ([a7baa25](https://github.com/phsmith/rundeck_exporter/commit/a7baa258ab6eeaf0112ba703f1d57187d5a7edf6))
* update CHANGELOG.md ([462f23d](https://github.com/phsmith/rundeck_exporter/commit/462f23d5881cc7ca141731fac13c1713a6840403))
* update CHANGELOG.md ([4c1d1eb](https://github.com/phsmith/rundeck_exporter/commit/4c1d1ebe1b1c227ccdfbf54f9a805b76470c7d97))
* update CHANGELOG.md ([64cb04c](https://github.com/phsmith/rundeck_exporter/commit/64cb04c6b6ccff530836c1f13a33457bf96ecbef))
* update CHANGELOG.md ([a23511e](https://github.com/phsmith/rundeck_exporter/commit/a23511e0df5019038c71c54b1ee3338b0ba8ed38))
* Update CHANGELOG.md ([9929bcc](https://github.com/phsmith/rundeck_exporter/commit/9929bcce08207dc435aa75b106d0c5e732e9d5f6))
* update docker-compose example grafana dashboard ([e96ca6a](https://github.com/phsmith/rundeck_exporter/commit/e96ca6af148c4f47a01bf74b731c4dafaf5c6546))
* update readme.md ([aa84e3d](https://github.com/phsmith/rundeck_exporter/commit/aa84e3d2c59a32e74d174f1a775655eb4161495b))
* update README.md ([3c6ce31](https://github.com/phsmith/rundeck_exporter/commit/3c6ce312e40b415bdf41b1b2783e097f1e4cfe54))
* update README.md ([8ceaa67](https://github.com/phsmith/rundeck_exporter/commit/8ceaa678b4a582b41601a02313f88b9dc861baa6))
* update README.md ([932dd8f](https://github.com/phsmith/rundeck_exporter/commit/932dd8f9ca923bc9aa790d38f8b02f61f7ef18ef))
* update README.md ([0ed23d4](https://github.com/phsmith/rundeck_exporter/commit/0ed23d4dc2fb06a715e0785c3648c3b4e92f98f6))
* update README.md ([18c7381](https://github.com/phsmith/rundeck_exporter/commit/18c73814f89d2a86f2432c4acf7e15ce7a4e199a))
* Update README.md ([88e4e62](https://github.com/phsmith/rundeck_exporter/commit/88e4e62dd87ec9ba883fe5e3f3d4f78eecae1cf9))
* Update README.md ([#32](https://github.com/phsmith/rundeck_exporter/issues/32)) ([0c1e60e](https://github.com/phsmith/rundeck_exporter/commit/0c1e60e549300c947191267725f5115700e5ab4a))
* Update Rundeck-Dashboard.json ([3daa191](https://github.com/phsmith/rundeck_exporter/commit/3daa191cf08048108c0c611b41f6fa15c782d480))
* update version ([7af1dbd](https://github.com/phsmith/rundeck_exporter/commit/7af1dbd27d83032714dfea179432a02c678bc1ee))


### Code Refactoring

* metrics collector cleanup, CI hardening, and Grafana fixes ([#129](https://github.com/phsmith/rundeck_exporter/issues/129)) ([e172d94](https://github.com/phsmith/rundeck_exporter/commit/e172d94a21f9ad1a6fd6a86ff244f6d535c987e6))

## [4.0.1](https://github.com/phsmith/rundeck_exporter/compare/v4.0.0...v4.0.1) (2026-06-15)


### Bug Fixes

* **ci:** fix release pipeline — draft releases, uv lock sync, and branch fix ([#134](https://github.com/phsmith/rundeck_exporter/issues/134)) ([8a02704](https://github.com/phsmith/rundeck_exporter/commit/8a027041ed8cd653c2b550aad7461a95c8555f63))
* **ci:** use PAT for release-please and add workflow_dispatch to release ([#132](https://github.com/phsmith/rundeck_exporter/issues/132)) ([9e6310c](https://github.com/phsmith/rundeck_exporter/commit/9e6310c39ee1de26edebc008fd55eddc97543d2f))

## [4.0.0](https://github.com/phsmith/rundeck_exporter/compare/v3.1.1...v4.0.0) (2026-06-15)


### ⚠ BREAKING CHANGES

* rundeck_project_executions_total renamed to rundeck_project_executions and type changed Counter→Gauge. Update dashboards, alerts, and recording rules referencing the old name.

### Code Refactoring

* metrics collector cleanup, CI hardening, and Grafana fixes ([#129](https://github.com/phsmith/rundeck_exporter/issues/129)) ([e172d94](https://github.com/phsmith/rundeck_exporter/commit/e172d94a21f9ad1a6fd6a86ff244f6d535c987e6))

## [Unreleased](https://github.com/phsmith/rundeck_exporter/compare/v3.1.1...HEAD)

## [v3.1.1](https://github.com/phsmith/rundeck_exporter/compare/v3.1.0...v3.1.1) - 2026-03-20

### What's Changed

* chore(helm): improve chart quality, CI validation, and release automation by @phsmith in https://github.com/phsmith/rundeck_exporter/pull/125
* fix(utils): replace requests with httpx for thread-safe HTTP clients by @phsmith in https://github.com/phsmith/rundeck_exporter/pull/127

**Full Changelog**: https://github.com/phsmith/rundeck_exporter/compare/v3.1.0...v3.1.1

## [v3.1.0](https://github.com/phsmith/rundeck_exporter/compare/v3.0.3...v3.1.0) - 2026-03-18

### What's Changed

* Fix update-changelog actions workflow by @phsmith in https://github.com/phsmith/rundeck_exporter/pull/121
* chore: code improvements, bug fixes, and project enhancements by @phsmith in https://github.com/phsmith/rundeck_exporter/pull/123
* feat: add option to export job options as execution metric labels by @tanmay-bhat in https://github.com/phsmith/rundeck_exporter/pull/112
* fix(ci): add write permissions for contents and packages in release by @phsmith in https://github.com/phsmith/rundeck_exporter/pull/124

### New Contributors

* @tanmay-bhat made their first contribution in https://github.com/phsmith/rundeck_exporter/pull/112

**Full Changelog**: https://github.com/phsmith/rundeck_exporter/compare/v3.0.3...v3.1.0

## [v3.0.3](https://github.com/phsmith/rundeck_exporter/compare/v3.0.2...v3.0.3) - 2025-11-07

## What's Changed

* Fix: rundeck_exporter exits if it is unable to reach the Rundeck host by @phsmith in https://github.com/phsmith/rundeck_exporter/pull/120

**Full Changelog**: https://github.com/phsmith/rundeck_exporter/compare/v3.0.2...v3.0.3

## [v3.0.2](https://github.com/phsmith/rundeck_exporter/compare/v3.0.1...v3.0.2) - 2025-09-02

## What's Changed

* Fix rundeck_exporter_args not properly parsing args by @phsmith in https://github.com/phsmith/rundeck_exporter/pull/117

**Full Changelog**: https://github.com/phsmith/rundeck_exporter/compare/v3.0.1...v3.0.2

## [v3.0.1](https://github.com/phsmith/rundeck_exporter/compare/v3.0.0...v3.0.1) - 2025-08-27

## What's Changed

* Update pr-checks workflow trigger by @phsmith in https://github.com/phsmith/rundeck_exporter/pull/115

**Full Changelog**: https://github.com/phsmith/rundeck_exporter/compare/v3.0.0...v3.0.1

## [v3.0.0](https://github.com/phsmith/rundeck_exporter/compare/v2.8.5...v3.0.0) - 2025-08-27

## What's Changed

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

### Fixed

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

## [2.5.0](https://github.com/phsmith/rundeck_exporter/compare/v2.4.14...v2.5.0) - 2022-09-29

### Added

- Added new metric `rundeck_project_executions_total`

### Fixed

- Fixed issue [#59](https://github.com/phsmith/rundeck_exporter/issues/59), unable to pass the RUNDECK_PROJECTS_FILTER environment variables
- Fixed issue [#65](https://github.com/phsmith/rundeck_exporter/issues/65), rundeck_project_execution_duration_seconds metric reporting wrong values. Instead of using the job `averageDuration` attribute, now the value is calculated based on the `start time` and `end time`

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

## [2.4.0](https://github.com/phsmith/rundeck_exporter/compare/v2.3.2...v2.4.0) - 2021-11-06

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
