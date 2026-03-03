# AGENTS.md

## Purpose
This repository hosts a Python-based Prometheus exporter for StashApp. The code is intentionally small and synchronous: metrics are fetched only during `/metrics` scrapes.

## Build / Run / Test / Lint
### Python runtime
- Install dependencies: `pip install -r requirements.txt`
- Run exporter locally: `python -m src.main`
- Environment variables:
  - `STASH_GRAPHQL_URL` (default `http://stash:9999/graphql`)
  - `STASH_API_KEY` (required)
  - `EXPORTER_LISTEN_PORT` (default `9100`)
  - `LOG_LEVEL` (default `INFO`)

### Docker image
- Build: `docker build -t stashapp-prometheus-exporter .`
- Run: `docker run --rm -p 9100:9100 -e STASH_GRAPHQL_URL=... -e STASH_API_KEY=... stashapp-prometheus-exporter`

### Tests
- No test runner is configured in this repo yet.
- If tests are added later, prefer `pytest` and keep them in `tests/`.
- Example single-test command (when pytest exists):
  - `python -m pytest tests/test_collector.py::test_collect_library_metrics`

### Lint / Format
- No lint or formatter is configured yet.
- If adding one, align with common Python tooling (ruff/black) and document the commands here.

## Project Layout
- `src/main.py`: entrypoint, HTTP server, signal handling
- `src/collector.py`: Prometheus Collector implementation
- `src/stash_client.py`: GraphQL client + error handling
- `src/config.py`: environment config + logging setup
- `src/queries.py`: GraphQL query strings
- `dashboards/`: Grafana dashboard JSON
- `METRICS.md`: metric descriptions

## Code Style (Python)
### Imports
- Use `from __future__ import annotations` at top of modules.
- Order imports: standard library, third-party, local imports, separated by blank lines.
- Prefer explicit imports over `import *`.

### Formatting
- Follow PEP 8 conventions for indentation and spacing (4 spaces, no tabs).
- Keep line lengths reasonable; wrap long call arguments across lines when needed.
- Use docstrings for modules/classes/functions (triple-quoted strings).

### Types
- Use type hints for function inputs/outputs and key variables.
- Prefer `Dict[str, Any]`, `Iterable[...]`, and `Optional[...]` where appropriate.
- Use `dataclass` for structured configuration or simple data containers.

### Naming
- `snake_case` for functions/variables.
- `PascalCase` for classes.
- Use descriptive names (`scrape_duration`, `stash_graphql_url`) instead of abbreviations.

### Error Handling
- Raise meaningful exceptions with context.
- Wrap network/JSON errors in `StashClientError` to normalize error handling.
- Guard against `None` or malformed data (`.get(...) or {}` / `or []`).

### Logging
- Use module-level logger: `LOG = logging.getLogger(__name__)`.
- Log at `info` for lifecycle events, `debug` for details, `error` for failures.
- Avoid printing directly except in early boot failures before logging config.

## Prometheus Exporter Rules (from `.cursor/rules/writing_prometheus_exporters.mdc`)
### Maintainability
- Prefer stable, maintainable metric mappings over exhaustive coverage.
- Keep metrics small and well-defined for a stable schema.

### Configuration
- Exporter should require minimal configuration beyond target URL/API key.
- Use YAML for exporter configuration if configuration files are introduced.

### Metric Naming
- Use `snake_case` and valid Prometheus characters `[a-zA-Z0-9:_]`.
- Include base units in metric names (`_seconds`, `_bytes`).
- Prefix metrics with `stash_`.
- Avoid `_sum`, `_count`, `_bucket`, `_total` unless implementing Summary/Histogram/Counter semantics.
- Do not encode label semantics in metric names (`*_by_type`) unless intentional.

### Labels
- Avoid high-cardinality labels and generic names (`type`, `region`, etc.).
- Do not use reserved labels `le` and `quantile`.
- Prefer separate metrics over labels for success/failure or read/write splits.
- Avoid combining unrelated values into one metric.

### Dropping/Transforming Metrics
- Avoid precomputed rates/percentages; let Prometheus compute rates.
- Avoid min/max/stddev unless strongly justified.
- Avoid re-exporting quantiles unless mapped to proper summaries.

### Collector Behavior
- Build metric families on each scrape; do not keep global state for scraped data.
- Avoid stale label values by creating metrics fresh each scrape.
- Exporter internal counters (e.g., scrape count) can persist across scrapes.
- Avoid duplicating Prometheus-provided metrics.

### Health Metrics
- Use `stash_up` to signal scrape success/failure.
- Emit scrape duration gauge (`stash_scrape_duration_seconds`).

### HTTP Interface
- Expose metrics on `/metrics` in Prometheus text format.
- Serve a simple root page linking to `/metrics` if HTML UI is added.

### Scheduling
- Scrape on demand (no periodic polling loops for metrics).
- Do not set explicit timestamps on samples.
- Document caching if expensive metrics are cached.

### Deployment
- Prefer one exporter per Stash instance/host.
- Let Prometheus handle service discovery.

## Contribution Guidance
- Keep changes minimal and focused.
- Preserve current stateless, synchronous scraping behavior.
- Update `METRICS.md` if adding or changing metric definitions.
- If you add tests or tooling, update this file with the exact commands.
