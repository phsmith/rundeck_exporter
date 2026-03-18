# Contributing to rundeck_exporter

Thank you for your interest in contributing. This document covers everything you need to get a working development environment, run the test suite, and submit a change.

## Table of Contents

- [Requirements](#requirements)
- [Development setup](#development-setup)
- [Project structure](#project-structure)
- [Running the exporter locally](#running-the-exporter-locally)
- [Testing](#testing)
- [Code style](#code-style)
- [Submitting changes](#submitting-changes)
- [Release process](#release-process)

---

## Requirements

| Tool | Purpose | Install |
| ---- | ------- | ------- |
| Python 3.11+ | Runtime | [python.org](https://www.python.org/downloads/) |
| [uv](https://docs.astral.sh/uv/) | Package management | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Docker + Compose | Integration tests, local Rundeck | [docs.docker.com](https://docs.docker.com/get-docker/) |
| Java 11+ | `rundeck-cli` (test project setup) | package manager of choice |

---

## Development setup

```bash
# Clone and enter the repo
git clone https://github.com/phsmith/rundeck_exporter.git
cd rundeck_exporter

# Create venv and install all dependencies (including dev)
uv sync --locked --all-extras --dev

# Verify the installation
uv run rundeck_exporter --help
```

---

## Project structure

```text
src/rundeck_exporter/
├── cli.py               # Entry point: argument validation, starts HTTP server
├── args.py              # Singleton argument parser (CLI + env vars)
├── constants.py         # Module-level constants and credential env vars
├── metrics_collector.py # Prometheus collector: collect(), get_project_executions(), etc.
└── utils.py             # HTTP helpers: request(), cached_request(), exit_with_msg()

tests/
└── test_rundeck_exporter_metrics.py  # Integration tests (require live Rundeck)

examples/
├── docker-compose/      # Full local stack: Rundeck + exporter + Prometheus + Grafana
├── grafana/             # Dashboard JSON
└── systemd/             # Systemd unit file example
```

All CLI arguments map to an environment variable — see `args.py` or run `rundeck_exporter --help` for the full list.

---

## Running the exporter locally

### With a live Rundeck (recommended)

The `examples/docker-compose/` directory contains a full stack with Rundeck, Prometheus, and Grafana:

```bash
# Start the full stack (Rundeck + Prometheus + Grafana)
make docker-compose-up

# Tail the exporter logs
make docker-compose-logs
make docker-compose-logs ARGS="-f rundeck_exporter"
```

Services exposed:

- Rundeck: <http://localhost:4440> (admin / admin)
- rundeck_exporter metrics: <http://localhost:9620/metrics>
- Prometheus: <http://localhost:9090>
- Grafana: <http://localhost:3000> (admin / admin)

To use your own Rundeck instance instead, run directly with env vars:

```bash
export RUNDECK_URL=http://your-rundeck:4440
export RUNDECK_TOKEN=your-api-token

uv run rundeck_exporter
```

---

## Testing

Integration tests require a running Rundeck instance with a pre-loaded test project. The CI workflow handles this automatically; for local runs use the Makefile targets:

```bash
# Start Rundeck, download rundeck-cli, and create the test project
make test-setup

# Run the test suite
make test

# Tear down when done
make test-teardown
```

### Run a single test

```bash
uv run pytest tests/test_rundeck_exporter_metrics.py::test_metric_rundeck_system_info -v
```

---

## Code style

The project uses [ruff](https://docs.astral.sh/ruff/) for linting and [mypy](https://mypy.readthedocs.io/) for static type checking. Maximum line length is **120 characters**.

```bash
# Lint
uv run ruff check src tests

# Auto-fix what's safe to fix
uv run ruff check --fix src tests

# Type check
uv run mypy src/
```

Both checks run automatically on every PR. A PR that fails either will not be merged.

---

## Submitting changes

1. **Fork** the repository and create a branch from `main`:

   ```bash
   git checkout -b fix/your-description
   ```

2. **Make your changes.** Keep commits focused — one logical change per commit.

3. **Lint, type-check, and test** before pushing:

   ```bash
   uv run ruff check src tests
   uv run mypy src/
   uv run pytest
   ```

4. **Open a pull request** against `main`. The PR title should be a short imperative sentence (e.g. `Fix session auth routing for /metrics/metrics`). Include a brief description of what changed and why.

5. PRs that touch only `*.md` or `LICENSE` files skip CI automatically (configured in `pr-checks.yml`).

### What makes a good PR

- One concern per PR — bug fix, feature, or refactor, not all three at once.
- New behaviour should come with a test or a clear explanation of why one isn't practical.
- If you're adding a new CLI argument, add it to `args.py` following the existing pattern (dotted `--rundeck.*` name, `RUNDECK_*` env var fallback, matching `dest=` name).

---

## Release process

Releases are fully automated via GitHub Actions. Only maintainers need the steps below.

1. Push a version tag to `main`:

   ```bash
   git tag v3.1.0
   git push origin v3.1.0
   ```

2. The `release.yml` workflow triggers automatically and:
   - Bumps the version in `pyproject.toml` and `uv.lock`, commits back to `main`
   - Builds and pushes the Docker image to Docker Hub and GHCR (tagged as `vX.Y.Z` and `latest` for non-pre-release tags)
   - Publishes the wheel to PyPI
   - Creates a GitHub release with auto-generated notes

3. The `update-changelog.yml` workflow then triggers on the published release and commits an updated `CHANGELOG.md` to `main`.

Pre-release tags (`alfa`, `beta` in the version string) skip the `:latest` Docker tag push.

### Required secrets

| Secret | Used by |
| ------ | ------- |
| `DEPLOY_KEY` | SSH key with write access to push version bump commits |
| `GH_RELEASE_TOKEN` | GitHub token for creating releases via `gh` CLI |
| `DOCKER_HUB_TOKEN` | Docker Hub push token |
| `TWINE_USERNAME` / `TWINE_PASSWORD` | PyPI upload credentials |
