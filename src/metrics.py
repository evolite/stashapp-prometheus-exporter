"""
Prometheus metric definitions and update helpers for the Stash exporter.

Metrics are intentionally low‑cardinality gauges that expose library‑wide
aggregates derived from the Stash GraphQL `stats` query and a small set of
Scene fields.

All metric names follow Prometheus best practices described in:
https://prometheus.io/docs/practices/naming/
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List

from prometheus_client import Gauge, Counter


# Primary library metrics
stash_scenes_total = Gauge(
    "stash_scenes_total",
    "Total number of scenes in the Stash library.",
)

stash_images_total = Gauge(
    "stash_images_total",
    "Total number of images in the Stash library.",
)

stash_performers_total = Gauge(
    "stash_performers_total",
    "Total number of performers in the Stash library.",
)

stash_studios_total = Gauge(
    "stash_studios_total",
    "Total number of studios in the Stash library.",
)

stash_files_total = Gauge(
    "stash_files_total",
    "Total number of files tracked by Stash.",
)

stash_files_size_bytes = Gauge(
    "stash_files_size_bytes",
    "Total size of all files tracked by Stash in bytes.",
)

stash_scenes_duration_seconds = Gauge(
    "stash_scenes_duration_seconds",
    "Total duration of all scenes in the Stash library in seconds.",
)

stash_galleries_total = Gauge(
    "stash_galleries_total",
    "Total number of galleries in the Stash library.",
)

stash_tags_total = Gauge(
    "stash_tags_total",
    "Total number of tags in the Stash library.",
)

stash_groups_total = Gauge(
    "stash_groups_total",
    "Total number of groups in the Stash library.",
)

stash_total_o_count = Gauge(
    "stash_total_o_count",
    "Total orgasm counter across all scenes (Stash o_counter aggregate).",
)

stash_total_play_duration_seconds = Gauge(
    "stash_total_play_duration_seconds",
    "Total play duration across all scenes in seconds.",
)

stash_total_play_count = Gauge(
    "stash_total_play_count",
    "Total number of scene plays recorded in Stash.",
)

stash_scenes_played_total = Gauge(
    "stash_scenes_played_total",
    "Total number of scenes that have at least one recorded play.",
)

# Coverage / curation metrics derived from Scene fields
stash_scenes_organized_total = Gauge(
    "stash_scenes_organized_total",
    "Total number of scenes marked as organized.",
)

stash_scenes_with_stashid_total = Gauge(
    "stash_scenes_with_stashid_total",
    "Total number of scenes that have at least one StashID entry.",
)

stash_scenes_tagged_total = Gauge(
    "stash_scenes_tagged_total",
    "Total number of scenes that have at least one tag.",
)

stash_scenes_with_performers_total = Gauge(
    "stash_scenes_with_performers_total",
    "Total number of scenes that have at least one performer.",
)

stash_scenes_with_studio_total = Gauge(
    "stash_scenes_with_studio_total",
    "Total number of scenes that have an associated studio.",
)

stash_scenes_watched_total = Gauge(
    "stash_scenes_watched_total",
    "Total number of scenes that have at least one play.",
)

stash_scenes_with_markers_total = Gauge(
    "stash_scenes_with_markers_total",
    "Total number of scenes that have at least one scene marker.",
)

stash_scene_markers_total = Gauge(
    "stash_scene_markers_total",
    "Total number of scene markers across all scenes.",
)

# Exporter health metric relative to Stash
stash_up = Gauge(
    "stash_up",
    "Whether the last scrape of Stash GraphQL succeeded (1 for success, 0 for failure).",
)

# Scrape performance metrics
stash_scrape_duration_seconds = Gauge(
    "stash_scrape_duration_seconds",
    "Time spent on the last scrape in seconds.",
)

stash_scrapes_total = Counter(
    "stash_scrapes_total",
    "Total number of scrapes attempted.",
    labelnames=("status",),
)


# Play duration buckets (derived from Scene.play_history)
stash_play_duration_seconds_by_dow = Gauge(
    "stash_play_duration_seconds_by_dow",
    "Total play duration bucketed by day of week in seconds.",
    labelnames=("day_of_week",),
)

stash_play_duration_seconds_by_hour = Gauge(
    "stash_play_duration_seconds_by_hour",
    "Total play duration bucketed by hour of day in seconds.",
    labelnames=("hour_of_day",),
)

stash_tag_usage_count = Gauge(
    "stash_tag_usage_count",
    "Number of played scenes using each tag.",
    labelnames=("tag_name",),
)

stash_orgasm_timestamp_seconds = Gauge(
    "stash_orgasm_timestamp_seconds",
    "Unix timestamp of orgasm events. Each orgasm from each scene is tracked as a separate time series with scene_id and orgasm_index labels.",
    labelnames=("scene_id", "orgasm_index"),
)


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def update_metrics_from_stats(stats: Dict[str, Any]) -> None:
    """Update Prometheus gauges from the `stats` query result.

    `stats` is expected to be the value of the `stats` field from the
    `LIBRARY_STATS_QUERY` in `queries.py`.
    """

    stash_scenes_total.set(_safe_int(stats.get("scene_count")))
    stash_images_total.set(_safe_int(stats.get("image_count")))
    stash_performers_total.set(_safe_int(stats.get("performer_count")))
    stash_studios_total.set(_safe_int(stats.get("studio_count")))

    # Approximate total file count and size by combining scene and image stats.
    # Stash exposes per‑type sizes, not a single aggregated files counter.
    scene_count = _safe_int(stats.get("scene_count"))
    image_count = _safe_int(stats.get("image_count"))
    scenes_size = _safe_int(stats.get("scenes_size"))
    images_size = _safe_int(stats.get("images_size"))

    stash_files_total.set(scene_count + image_count)
    stash_files_size_bytes.set(scenes_size + images_size)

    # Aggregate duration and additional library counts
    stash_scenes_duration_seconds.set(_safe_int(stats.get("scenes_duration")))
    stash_galleries_total.set(_safe_int(stats.get("gallery_count")))
    stash_tags_total.set(_safe_int(stats.get("tag_count")))
    stash_groups_total.set(_safe_int(stats.get("group_count")))

    # Aggregate engagement metrics
    stash_total_o_count.set(_safe_int(stats.get("total_o_count")))
    stash_total_play_duration_seconds.set(_safe_int(stats.get("total_play_duration")))
    stash_total_play_count.set(_safe_int(stats.get("total_play_count")))
    stash_scenes_played_total.set(_safe_int(stats.get("scenes_played")))


_DOW_NAMES: List[str] = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _parse_utc_timestamp(value: str) -> datetime | None:
    """Parse a Stash UTC timestamp (e.g. 2025-12-12T20:07:59Z) to a datetime.

    Returns None if parsing fails.
    """

    if not value:
        return None
    try:
        # Normalise Z suffix to ISO 8601 offset format.
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def update_playtime_buckets_from_scenes(scenes: Iterable[Dict[str, Any]]) -> None:
    """Update play duration buckets from a list of Scene objects.

    `scenes` is expected to be the value of `findScenes.scenes` from the
    `SCENE_PLAY_HISTORY_QUERY` in `queries.py`. This function aggregates
    total play duration per day-of-week and per hour-of-day.
    """

    dow_totals: Dict[str, float] = {name: 0.0 for name in _DOW_NAMES}
    hour_totals: Dict[str, float] = {str(h): 0.0 for h in range(24)}

    for scene in scenes:
        play_count = _safe_int(scene.get("play_count"))
        total_duration = float(scene.get("play_duration") or 0.0)
        history = scene.get("play_history") or []

        if play_count <= 0 or total_duration <= 0.0:
            continue
        if not history:
            continue

        # Approximate per-play duration by evenly splitting across history entries.
        # Use the larger of play_count and history length to avoid division by zero
        # and obviously wrong scaling.
        divisor = max(play_count, len(history))
        per_play_duration = total_duration / float(divisor)

        for ts in history:
            dt = _parse_utc_timestamp(str(ts))
            if dt is None:
                continue

            dow_index = dt.weekday()
            if 0 <= dow_index < len(_DOW_NAMES):
                dow_name = _DOW_NAMES[dow_index]
                dow_totals[dow_name] += per_play_duration

            hour_key = str(dt.hour)
            hour_totals[hour_key] += per_play_duration

    for dow_name, total_seconds in dow_totals.items():
        stash_play_duration_seconds_by_dow.labels(day_of_week=dow_name).set(total_seconds)

    for hour_key, total_seconds in hour_totals.items():
        stash_play_duration_seconds_by_hour.labels(hour_of_day=hour_key).set(total_seconds)


def update_metadata_from_scenes(scenes: Iterable[Dict[str, Any]]) -> None:
    """Update metadata/coverage metrics from a list of Scene objects."""

    organized = 0
    with_stashid = 0
    tagged = 0
    with_performers = 0
    with_studio = 0
    watched = 0
    with_markers = 0
    marker_total = 0

    for scene in scenes:
        if scene.get("organized"):
            organized += 1

        stash_ids = scene.get("stash_ids") or []
        if stash_ids:
            with_stashid += 1

        tags = scene.get("tags") or []
        if tags:
            tagged += 1

        performers = scene.get("performers") or []
        if performers:
            with_performers += 1

        studio = scene.get("studio")
        if studio is not None:
            with_studio += 1

        play_count = _safe_int(scene.get("play_count"))
        if play_count > 0:
            watched += 1

        markers = scene.get("scene_markers") or []
        if markers:
            with_markers += 1
            try:
                marker_total += len(markers)
            except TypeError:
                # In case markers is not a simple list, fall back to one per entry
                marker_total += sum(1 for _ in markers)

    stash_scenes_organized_total.set(float(organized))
    stash_scenes_with_stashid_total.set(float(with_stashid))
    stash_scenes_tagged_total.set(float(tagged))
    stash_scenes_with_performers_total.set(float(with_performers))
    stash_scenes_with_studio_total.set(float(with_studio))
    stash_scenes_watched_total.set(float(watched))
    stash_scenes_with_markers_total.set(float(with_markers))
    stash_scene_markers_total.set(float(marker_total))


def update_tag_usage_from_scenes(scenes: Iterable[Dict[str, Any]]) -> None:
    """Update tag usage metrics from played scene data.

    `scenes` is expected to be the value of `findScenes.scenes` from the
    `SCENE_PLAY_HISTORY_QUERY` in `queries.py`. Tag names are included
    directly in the scene data.

    This function counts how many played scenes (scenes with play_count > 0)
    use each tag and updates the `stash_tag_usage_count` metric with tag names
    as labels. This provides dynamic, engagement-based tag popularity metrics
    based only on played scenes.

    Only the top 100 tags by usage count are exported to limit label cardinality.
    """

    # Count tag usage only from played scenes
    tag_usage_counts: Dict[str, int] = {}

    for scene in scenes:
        # Only count tags from scenes that have been played
        play_count = _safe_int(scene.get("play_count"))
        if play_count <= 0:
            continue

        scene_tags = scene.get("tags") or []
        for tag_obj in scene_tags:
            tag_name = str(tag_obj.get("name", ""))
            if tag_name:
                tag_usage_counts[tag_name] = tag_usage_counts.get(tag_name, 0) + 1

    # Sort by count (descending) and take top 100 to limit label cardinality
    sorted_tags = sorted(tag_usage_counts.items(), key=lambda x: x[1], reverse=True)
    top_tags = sorted_tags[:100]

    # Update metrics only for top 100 tags
    for tag_name, count in top_tags:
        stash_tag_usage_count.labels(tag_name=tag_name).set(float(count))


def update_orgasm_history_from_scenes(scenes: Iterable[Dict[str, Any]]) -> None:
    """Update orgasm timestamp metrics from scene data.

    `scenes` is expected to be the value of `findScenes.scenes` from the
    `SCENE_PLAY_HISTORY_QUERY` in `queries.py`. This function processes
    `o_history` from all scenes and exports each orgasm timestamp as a
    separate time series.

    Each orgasm event is tracked as a Gauge set to the Unix timestamp,
    allowing Grafana to plot all orgasm events over time as a unified history.
    Multiple orgasms from the same scene are tracked using an orgasm_index
    label to differentiate them.
    """

    # Collect all orgasm events across all scenes
    # Structure: scene_id -> list of (timestamp, index) tuples
    scene_orgasms: Dict[str, List[float]] = {}

    for scene in scenes:
        scene_id = str(scene.get("id", ""))
        if not scene_id:
            continue

        o_history = scene.get("o_history") or []
        if not o_history:
            continue

        # Parse and collect all orgasm timestamps for this scene
        timestamps = []
        for timestamp_str in o_history:
            dt = _parse_utc_timestamp(str(timestamp_str))
            if dt is None:
                continue
            # Convert to Unix timestamp (seconds since epoch)
            unix_timestamp = dt.timestamp()
            timestamps.append(unix_timestamp)

        if timestamps:
            # Sort timestamps to ensure consistent indexing (oldest first)
            timestamps.sort()
            scene_orgasms[scene_id] = timestamps

    # Update metrics: each orgasm gets its own time series using scene_id + orgasm_index
    for scene_id, timestamps in scene_orgasms.items():
        for index, timestamp in enumerate(timestamps):
            # Use orgasm_index starting from 0 for each scene
            # This allows tracking all orgasms from all scenes as a unified history
            stash_orgasm_timestamp_seconds.labels(scene_id=scene_id, orgasm_index=str(index)).set(timestamp)


__all__ = [
    "stash_scenes_total",
    "stash_images_total",
    "stash_performers_total",
    "stash_studios_total",
    "stash_files_total",
    "stash_files_size_bytes",
    "stash_scenes_duration_seconds",
    "stash_galleries_total",
    "stash_tags_total",
    "stash_groups_total",
    "stash_total_o_count",
    "stash_total_play_duration_seconds",
    "stash_total_play_count",
    "stash_scenes_played_total",
    "stash_scenes_organized_total",
    "stash_scenes_with_stashid_total",
    "stash_scenes_tagged_total",
    "stash_scenes_with_performers_total",
    "stash_scenes_with_studio_total",
    "stash_scenes_watched_total",
    "stash_scenes_with_markers_total",
    "stash_scene_markers_total",
    "stash_play_duration_seconds_by_dow",
    "stash_play_duration_seconds_by_hour",
    "stash_tag_usage_count",
    "stash_up",
    "stash_scrape_duration_seconds",
    "stash_scrapes_total",
    "update_metrics_from_stats",
    "update_playtime_buckets_from_scenes",
    "update_metadata_from_scenes",
    "update_tag_usage_from_scenes",
    "update_orgasm_history_from_scenes",
    "stash_orgasm_timestamp_seconds",
]

