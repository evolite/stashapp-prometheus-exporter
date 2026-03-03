# StashApp Prometheus Exporter

A Prometheus exporter for StashApp that exposes your library stats, play patterns, performer demographics and engagement metrics via GraphQL. 

## Quick Start

```bash
podman run --rm -p 9100:9100 \
  -e STASH_GRAPHQL_URL="http://stash:9999/graphql" \
  -e STASH_API_KEY="your_api_key" \
  ghcr.io/evolite/stashapp-prometheus-exporter:latest
```

Point Prometheus at `http://localhost:9100/metrics` and you're good to go.

## Configuration

- `STASH_GRAPHQL_URL` - Stash GraphQL endpoint (default: `http://stash:9999/graphql`)
- `STASH_API_KEY` - Your Stash API key (required)
- `EXPORTER_LISTEN_PORT` - Metrics port (default: `9100`)
- `LOG_LEVEL` - Python log level (default: `INFO`)

## Metrics

All metrics are prefixed with `stash_` and follow Prometheus naming conventions. See [METRICS.md](METRICS.md) for detailed documentation of all available metrics.

## Example Queries

```promql
# Top 10 scenes by o-count
topk(10, stash_scene_o_counter)

# Total o-count events in the last hour
sum(increase(stash_scene_o_counter[1h]))

# Average watch time per play
stash_total_play_duration_seconds / clamp_max(stash_total_play_count, 1e9)

# Play duration by day of week (in hours)
stash_play_duration_seconds_by_dow / 3600

# Most active watching hour
topk(1, stash_play_duration_seconds_by_hour)

# Library organization coverage
stash_scenes_organized_total / stash_scenes_total * 100

# Scenes with StashID coverage
stash_scenes_with_stashid_total / stash_scenes_total * 100

# Total library size in GB
stash_files_size_bytes / 1024 / 1024 / 1024

# Average scene duration
stash_scenes_duration_seconds / stash_scenes_total

# Most popular tags (top 10)
topk(10, stash_tag_usage_count)
```

## Dashboard

Check out `dashboards/stashapp-overview.json` for a ready-to-use Grafana dashboard that visualizes all these metrics. Just import it into Grafana and you're set!

All queries are based on the [public Stash GraphQL API documentation](https://docs.stashapp.cc/api).

---

Happy monitoring! 📊
