# StashApp Prometheus Exporter

Prometheus exporter for StashApp that exposes library stats, curation coverage, and playtime metrics via GraphQL.

## What it does

Queries your Stash instance and exposes metrics like total scenes, images, performers, watch time, play patterns (by day of week and hour of day), and how well your library is organized (organized flag, tags, performers, studios, stashids, markers) on `/metrics` for Prometheus to scrape.

These queries are based on the public Stash GraphQL API documentation (`https://docs.stashapp.cc/api`) and are intended to return cheap, aggregated statistics suitable for exporter usage.

## Run with Docker / Podman

```bash
podman run --rm -p 9100:9100 \
  -e STASH_GRAPHQL_URL="http://stash:9999/graphql" \
  -e STASH_API_KEY="your_api_key" \
  ghcr.io/evolite/stashapp-prometheus-exporter:latest
```

For a complete stack example with Stash, Prometheus, and Grafana, see `podman-compose.yml` in this repository.

## Configuration

- `STASH_GRAPHQL_URL` - Stash GraphQL endpoint (default: `http://stash:9999/graphql`)
- `STASH_API_KEY` - Your Stash API key (required)
- `SCRAPE_INTERVAL_SECONDS` - How often to query Stash (default: `30`)
- `EXPORTER_LISTEN_PORT` - Metrics port (default: `9100`)

## Metrics

### Library statistics
- `stash_scenes_total` - Total scenes
- `stash_images_total` - Total images
- `stash_galleries_total` - Total galleries
- `stash_performers_total` - Total performers
- `stash_studios_total` - Total studios
- `stash_tags_total` - Total tags
- `stash_groups_total` - Total groups
- `stash_files_total` - Total files (scenes + images)
- `stash_files_size_bytes` - Total file size in bytes
- `stash_scenes_duration_seconds` - Total scene duration in seconds

### Curation / coverage
- `stash_scenes_organized_total` - Scenes marked as organized
- `stash_scenes_with_stashid_total` - Scenes with at least one StashID
- `stash_scenes_tagged_total` - Scenes with at least one tag
- `stash_scenes_with_performers_total` - Scenes with at least one performer
- `stash_scenes_with_studio_total` - Scenes with a studio
- `stash_scenes_watched_total` - Scenes with at least one play
- `stash_scenes_with_markers_total` - Scenes with at least one marker
- `stash_scene_markers_total` - Total number of scene markers

You can derive the "missing" side and ratios in PromQL, for example:

- Unorganized scenes: `stash_scenes_total - stash_scenes_organized_total`
- StashID coverage: `stash_scenes_with_stashid_total / stash_scenes_total`

### Play statistics
- `stash_total_play_count` - Total number of scene plays
- `stash_total_play_duration_seconds` - Total play duration across all scenes in seconds
- `stash_scenes_played_total` - Scenes that have at least one recorded play
- `stash_total_o_count` - Total orgasm counter across all scenes

### Playtime patterns
- `stash_play_duration_seconds_by_dow{day_of_week}` - Play duration by day of week (Mon, Tue, Wed, Thu, Fri, Sat, Sun)
- `stash_play_duration_seconds_by_hour{hour_of_day}` - Play duration by hour of day (0-23)

### Exporter health
- `stash_up` - 1 if the last scrape of Stash GraphQL succeeded, 0 otherwise
- `stash_scrape_duration_seconds` - Time spent on the last scrape in seconds
- `stash_scrapes_total{status="success|failure"}` - Total number of scrape attempts

See `dashboards/stashapp-overview.json` for a Grafana dashboard that uses all of these.

Images are automatically built and pushed to GHCR on pushes to `main` and version tags.
