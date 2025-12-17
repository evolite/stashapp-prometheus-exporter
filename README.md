## StashApp Prometheus Exporter

Small Prometheus exporter that queries a StashApp instance via GraphQL and exposes library‑wide metrics on a `/metrics` HTTP endpoint.

The container image is intended to be published to GitHub Container Registry (GHCR) and deployed alongside Stash, Prometheus, and Grafana (for example via `podman-compose`).

### Metrics

The exporter currently exposes low‑cardinality Gauges derived from a single aggregated `stats` query:

- **stash_scenes_total**: Total number of scenes in the library.
- **stash_images_total**: Total number of images in the library.
- **stash_performers_total**: Total number of performers in the library.
- **stash_studios_total**: Total number of studios in the library.
- **stash_files_total**: Total number of files tracked by Stash.
- **stash_files_size_bytes**: Total size of all files tracked by Stash in bytes.
- **stash_up**: `1` if the last scrape from Stash GraphQL succeeded, otherwise `0`.

Metric naming follows the Prometheus exporter best practices described in `https://prometheus.io/docs/instrumenting/writing_exporters/`.

### Configuration

The exporter is configured entirely through environment variables:

- **STASH_GRAPHQL_URL**: Stash GraphQL endpoint URL.  
  Default: `http://stash:9999/graphql`
- **STASH_API_KEY**: Stash API key with permission to access the GraphQL API.  
  Required, no default.
- **SCRAPE_INTERVAL_SECONDS**: Interval between scrapes from Stash.  
  Default: `30`
- **EXPORTER_LISTEN_PORT**: Port for the `/metrics` HTTP server.  
  Default: `9100`
- **LOG_LEVEL**: Python log level name (for example `INFO`, `DEBUG`).  
  Default: `INFO`

### Running locally (no containers)

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export STASH_GRAPHQL_URL="http://localhost:9999/graphql"
export STASH_API_KEY="your_api_key_here"

python -m src.main
```

Then scrape metrics from `http://localhost:9100/metrics`.

### Running with Podman or Docker directly

Build the image:

```bash
podman build -t stashapp-prometheus-exporter:local .
```

Run the exporter:

```bash
podman run --rm \
  -p 9100:9100 \
  -e STASH_GRAPHQL_URL="http://host.containers.internal:9999/graphql" \
  -e STASH_API_KEY="your_api_key_here" \
  stashapp-prometheus-exporter:local
```

Adjust the `STASH_GRAPHQL_URL` value to match where Stash is reachable from inside the container.

### podman-compose example

An example stack is provided in [`podman-compose.yml`](podman-compose.yml) and [`prometheus.yml`](prometheus.yml).

Start the whole stack:

```bash
export STASH_API_KEY="your_api_key_here"
podman-compose up -d
```

This will start:

- `stash` on `http://localhost:9999`
- `stash-exporter` on `http://localhost:9100`
- `prometheus` on `http://localhost:9090`
- `grafana` on `http://localhost:3000`

The Prometheus configuration in [`prometheus.yml`](prometheus.yml) includes a `stashapp` job that scrapes the exporter at `stash-exporter:9100`.

### GitHub Actions and GHCR

The workflow in [`.github/workflows/build-and-publish.yml`](.github/workflows/build-and-publish.yml) builds the Docker image and pushes it to GHCR using `GITHUB_TOKEN`:

- Pushes to `main` build and push:
  - `ghcr.io/<owner>/stashapp-prometheus-exporter:latest`
  - `ghcr.io/<owner>/stashapp-prometheus-exporter:<git-sha>`
- Tag pushes matching `v*` additionally build and push:
  - `ghcr.io/<owner>/stashapp-prometheus-exporter:<tag>`

Make sure GitHub Actions has `packages: write` permission enabled for this repository.


