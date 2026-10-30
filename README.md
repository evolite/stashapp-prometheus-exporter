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
  ghcr.io/evolite/stashapp-prometheus-exporter:latest
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

An **opinionated** dashboard is provided in `dashboards/stashapp-overview.json`. Treat it as a starting point or use it as is.

- Sections are ordered by how often they are likely to be checked: **Health**, **Library Overview**, **Engagement & Playback**,
  **Library Curation**, **Playtime Patterns**, **Scene Quality**, **Performer Demographics**.
- It is deliberately library-focused: it does not show per-performer favourites or rankings.
- Import via Dashboards → Import in Grafana and pick your Prometheus data source when asked.
- The Health tile matches any scrape job named `stash*` (the example `prometheus-example.yml` uses `stash`).
- Built and used on Grafana 13.2

<img width="2012" height="1234" alt="image" src="https://github.com/user-attachments/assets/b39de60c-3ad8-4e1c-b040-1e8210b31244" />


## Source

[github.com/evolite/stashapp-prometheus-exporter](https://github.com/evolite/stashapp-prometheus-exporter)
