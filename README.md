# StashApp Prometheus Exporter

Prometheus exporter for StashApp that exposes library stats and playtime metrics via GraphQL.

## What it does

Queries your Stash instance and exposes metrics like total scenes, images, performers, watch time, and play patterns (by day of week and hour of day) on `/metrics` for Prometheus to scrape.

## Quick start

### Docker/Podman

```bash
podman run --rm -p 9100:9100 \
  -e STASH_GRAPHQL_URL="http://stash:9999/graphql" \
  -e STASH_API_KEY="your_api_key" \
  ghcr.io/evolite/stashapp-prometheus-exporter:latest
```

## Configuration

- `STASH_GRAPHQL_URL` - Stash GraphQL endpoint (default: `http://stash:9999/graphql`)
- `STASH_API_KEY` - Your Stash API key (required)
- `SCRAPE_INTERVAL_SECONDS` - How often to query Stash (default: `30`)
- `EXPORTER_LISTEN_PORT` - Metrics port (default: `9100`)

## Metrics

Main metrics: `stash_scenes_total`, `stash_images_total`, `stash_performers_total`, `stash_total_play_count`, `stash_total_play_duration_seconds`, plus playtime patterns by day of week and hour of day.

See `dashboards/stashapp-overview.json` for a Grafana dashboard example.

![Dashboard Example](docs/dashboard.png)

Images are automatically built and pushed to GHCR on pushes to `main` and version tags.


