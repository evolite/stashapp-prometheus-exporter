# StashApp Prometheus Exporter

Prometheus exporter for StashApp that exposes library stats and playtime metrics via GraphQL.

## What it does

Queries your Stash instance and exposes metrics like total scenes, images, performers, watch time, and play patterns (by day of week and hour of day) on `/metrics` for Prometheus to scrape.

These queries are based on the public Stash GraphQL API documentation (`https://docs.stashapp.cc/api/?utm_source=openai`) and are intended to return cheap, aggregated statistics suitable for exporter usage.

### Docker/Podman

```bash
podman run --rm -p 9100:9100 \
  -e STASH_GRAPHQL_URL="http://stash:9999/graphql" \
  -e STASH_API_KEY="your_api_key" \
  ghcr.io/evolite/stashapp-prometheus-exporter:latest
```

### Docker Compose / Podman Compose

Create a `docker-compose.yml` or `podman-compose.yml` file:

```yaml
services:
  stash-exporter:
    image: ghcr.io/evolite/stashapp-prometheus-exporter:latest
    container_name: stash-exporter
    environment:
      STASH_GRAPHQL_URL: http://stash:9999/graphql
      STASH_API_KEY: ${STASH_API_KEY}
      SCRAPE_INTERVAL_SECONDS: "30"
    ports:
      - "9100:9100"
    depends_on:
      - stash
    restart: unless-stopped
```

Then run:
```bash
docker-compose up -d
# or
podman-compose up -d
```

For a complete stack example with Stash, Prometheus, and Grafana, see `podman-compose.yml` in this repository.

## Configuration

- `STASH_GRAPHQL_URL` - Stash GraphQL endpoint (default: `http://stash:9999/graphql`)
- `STASH_API_KEY` - Your Stash API key (required)
- `SCRAPE_INTERVAL_SECONDS` - How often to query Stash (default: `30`)
- `EXPORTER_LISTEN_PORT` - Metrics port (default: `9100`)

## Metrics

The exporter collects the following metrics from your Stash instance:

### Library Statistics
- `stash_scenes_total` - Total number of scenes
- `stash_images_total` - Total number of images
- `stash_galleries_total` - Total number of galleries
- `stash_performers_total` - Total number of performers
- `stash_studios_total` - Total number of studios
- `stash_tags_total` - Total number of tags
- `stash_groups_total` - Total number of groups
- `stash_files_total` - Total number of files (scenes + images)
- `stash_files_size_bytes` - Total size of all files in bytes
- `stash_scenes_duration_seconds` - Total duration of all scenes in seconds

### Play Statistics
- `stash_total_play_count` - Total number of scene plays recorded
- `stash_total_play_duration_seconds` - Total play duration across all scenes in seconds
- `stash_scenes_played_total` - Number of scenes that have at least one recorded play
- `stash_total_o_count` - Total orgasm counter across all scenes

### Playtime Patterns
- `stash_play_duration_seconds_by_dow{day_of_week}` - Play duration by day of week (Mon, Tue, Wed, Thu, Fri, Sat, Sun)
- `stash_play_duration_seconds_by_hour{hour_of_day}` - Play duration by hour of day (0-23)

### Exporter Health
- `stash_up` - Whether the last scrape of Stash GraphQL succeeded (1 for success, 0 for failure)

See `dashboards/stashapp-overview.json` for a Grafana dashboard example.

Images are automatically built and pushed to GHCR on pushes to `main` and version tags.