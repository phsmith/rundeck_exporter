# AGENTS.md

This file provides guidance AI agents when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run tests (requires a live Rundeck instance; see CI setup below)
uv run pytest

# Run a single test
uv run pytest tests/test_rundeck_exporter_metrics.py::test_metric_rundeck_system_info

# Lint
uv run ruff check src tests

# Build Docker image
make docker-build

# Start example environment
make local-env-setup
```

Tests require a live Rundeck instance. In CI, this is started via `examples/docker-compose/docker-compose-ci.yml`. Test environment variables are configured in `pyproject.toml` under `[tool.pytest.ini_options]` (pointing to `http://localhost:4440` with token `exporter_admin_auth_token`).

## Architecture

This is a Prometheus exporter for Rundeck metrics. It follows the standard Prometheus collector pattern:

1. **`cli.py`** — Entry point. Parses and validates args (URL, auth), then starts a Prometheus HTTP server on port 9620 and registers the collector.

2. **`args.py`** — Singleton `RundeckExporterArgs` using argparse with dotted-notation CLI flags (e.g., `--rundeck.url`) and environment variable fallbacks. All flags map to `RUNDECK_*` env vars.

3. **`metrics_collector.py`** — Core class `RundeckMetricsCollector` implements `prometheus_client.core.Collector`. Its `collect()` method is called by the Prometheus HTTP server on each scrape. Uses `ThreadPoolExecutor` for parallel per-project execution data fetching.

4. **`utils.py`** — HTTP helpers: `request()` for direct Rundeck API calls (token or session auth), `cached_request()` wrapping with `cachetools.TTLCache` (TTL configurable via `--rundeck.cached.requests.ttl`).

**Data flow:**
`/metrics` scrape → `collect()` → `request()`/`cached_request()` → Rundeck REST API endpoints (`/system/info`, `/metrics/metrics`, `/projects`, `/executions`, `/resources`)

**Auth:** supports both `--rundeck.token` (header `X-Rundeck-Auth-Token`) and username/password (`--rundeck.username`/`--rundeck.password`, using session-based auth).

## Key Design Notes

- The args singleton is instantiated at import time (`args.py` bottom), so test setup must set env vars before importing the module.
- `cached_request()` is used for system-level endpoints; per-project execution calls use `request()` directly.
- The collector is registered globally with `prometheus_client.REGISTRY`; tests use a module-scoped fixture to register once and share across tests.
- Line length limit is 120 characters (ruff).
