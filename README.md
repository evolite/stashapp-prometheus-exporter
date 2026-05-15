# stashapp-prometheus-exporter

Prometheus exporter for [Stash](https://stashapp.cc) — exposes library stats, play history, performer demographics, and more as Prometheus metrics.

## Quickstart

### Docker / Podman

```sh
docker run -d \
  --name stash-exporter \
  -e STASH_GRAPHQL_URL=http://stash:9999/graphql \
  -e STASH_API_KEY=your_api_key \
  -p 9100:9100 \
  codeberg.org/surging9143/stashapp-prometheus-exporter:latest
```

Metrics will be available at `http://localhost:9100/metrics`.

### Compose

Copy `podman-compose-example.yml`, fill in your `STASH_API_KEY`, and run:

```sh
podman-compose -f podman-compose-example.yml up -d
```

### Prometheus config

Add a scrape job to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: stash
    static_configs:
      - targets: ['stash-exporter:9100']
```

See `prometheus-example.yml` for a full example.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `STASH_GRAPHQL_URL` | `http://stash:9999/graphql` | Stash GraphQL endpoint |
| `STASH_API_KEY` | — | Stash API key (Settings → Security) |
| `SCRAPE_INTERVAL_SECONDS` | `30` | How often to poll Stash |
| `EXPORTER_LISTEN_PORT` | `9100` | Port to expose `/metrics` on |
| `LOG_LEVEL` | `INFO` | Python log level |

## Metrics

See [METRICS.md](METRICS.md) for the full list of exported metrics.

## Grafana

A pre-built dashboard is available in `dashboards/stashapp-overview.json`. Import it via Dashboards → Import in Grafana.

## Source

[codeberg.org/surging9143/stashapp-prometheus-exporter](https://codeberg.org/surging9143/stashapp-prometheus-exporter)
