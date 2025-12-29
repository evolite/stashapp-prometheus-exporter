"""
Custom Prometheus Collector for synchronous scraping.

This collector implements the Prometheus best practice of synchronous scraping:
metrics are only collected when Prometheus requests them, not on a timer.

All labeled metrics use MetricFamily objects to ensure stale labels are automatically
cleared when they no longer appear in the data.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any, Dict, Iterable

from prometheus_client.core import GaugeMetricFamily
from prometheus_client import Counter

from .queries import LIBRARY_STATS_QUERY, SCENE_PLAY_HISTORY_QUERY
from .stash_client import StashClient, StashClientError

# Exporter-specific counter that persists across scrapes
# This tracks exporter behavior, not Stash data, so it's acceptable to use
# a regular Counter instance rather than MetricFamily
stash_scrapes_total = Counter(
    "stash_scrapes_total",
    "Total number of scrapes attempted.",
    labelnames=("status",),
)


LOG = logging.getLogger(__name__)

_DOW_NAMES: list[str] = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _safe_int(value: Any) -> int:
    """Safely convert a value to int, returning 0 on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


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


class StashCollector:
    """Custom Prometheus Collector that synchronously scrapes Stash on each /metrics request.

    This collector follows Prometheus best practices by:
    - Scraping only when Prometheus requests metrics (synchronous)
    - Using MetricFamily objects for labeled metrics to avoid stale labels
    - Being fully stateless (no cached data between scrapes)
    """

    def __init__(self, client: StashClient):
        """Initialize the collector with a Stash client."""
        self.client = client

    def collect(self) -> Iterable[GaugeMetricFamily | CounterMetricFamily]:
        """Collect metrics from Stash. Called by Prometheus on each scrape.

        This method is called synchronously when Prometheus requests /metrics.
        All data is fetched fresh from Stash - no caching or state is maintained.
        """
        scrape_start = time.monotonic()
        scrape_success = False

        try:
            # Fetch library stats
            stats_data: Dict[str, Any] = self.client.run_query(LIBRARY_STATS_QUERY)
            stats = stats_data.get("stats") or {}

            # Fetch scene data for detailed metrics
            scenes_data: Dict[str, Any] = self.client.run_query(SCENE_PLAY_HISTORY_QUERY)
            scenes_root = scenes_data.get("findScenes") or {}
            scenes = scenes_root.get("scenes") or []

            scrape_success = True

            # Yield all metrics
            yield from self._collect_library_metrics(stats)
            yield from self._collect_playtime_metrics(scenes)
            yield from self._collect_metadata_metrics(scenes)
            yield from self._collect_tag_usage_metrics(scenes)
            yield from self._collect_orgasm_metrics(scenes)
            yield from self._collect_exporter_health_metrics(scrape_success, time.monotonic() - scrape_start)

            # Increment scrape counter (persists across scrapes)
            stash_scrapes_total.labels(status="success").inc()

        except StashClientError as exc:
            LOG.error("Failed to scrape Stash GraphQL: %s", exc)
            # Still yield exporter health metrics to indicate failure
            yield from self._collect_exporter_health_metrics(False, time.monotonic() - scrape_start)
            # Increment failure counter
            stash_scrapes_total.labels(status="failure").inc()

    def _collect_library_metrics(self, stats: Dict[str, Any]) -> Iterable[GaugeMetricFamily]:
        """Collect library-wide aggregate metrics from stats query."""
        # Primary library metrics
        yield GaugeMetricFamily("stash_scenes_total", "Total number of scenes in the Stash library.", value=_safe_int(stats.get("scene_count")))
        yield GaugeMetricFamily("stash_images_total", "Total number of images in the Stash library.", value=_safe_int(stats.get("image_count")))
        yield GaugeMetricFamily("stash_performers_total", "Total number of performers in the Stash library.", value=_safe_int(stats.get("performer_count")))
        yield GaugeMetricFamily("stash_studios_total", "Total number of studios in the Stash library.", value=_safe_int(stats.get("studio_count")))
        yield GaugeMetricFamily("stash_galleries_total", "Total number of galleries in the Stash library.", value=_safe_int(stats.get("gallery_count")))
        yield GaugeMetricFamily("stash_tags_total", "Total number of tags in the Stash library.", value=_safe_int(stats.get("tag_count")))
        yield GaugeMetricFamily("stash_groups_total", "Total number of groups in the Stash library.", value=_safe_int(stats.get("group_count")))

        # Approximate total file count and size by combining scene and image stats
        scene_count = _safe_int(stats.get("scene_count"))
        image_count = _safe_int(stats.get("image_count"))
        scenes_size = _safe_int(stats.get("scenes_size"))
        images_size = _safe_int(stats.get("images_size"))

        yield GaugeMetricFamily("stash_files_total", "Total number of files tracked by Stash.", value=scene_count + image_count)
        yield GaugeMetricFamily("stash_files_size_bytes", "Total size of all files tracked by Stash in bytes.", value=scenes_size + images_size)
        yield GaugeMetricFamily("stash_scenes_duration_seconds", "Total duration of all scenes in the Stash library in seconds.", value=_safe_int(stats.get("scenes_duration")))

        # Aggregate engagement metrics
        yield GaugeMetricFamily("stash_total_o_count", "Total orgasm counter across all scenes (Stash o_counter aggregate).", value=_safe_int(stats.get("total_o_count")))
        yield GaugeMetricFamily("stash_total_play_duration_seconds", "Total play duration across all scenes in seconds.", value=_safe_int(stats.get("total_play_duration")))
        yield GaugeMetricFamily("stash_total_play_count", "Total number of scene plays recorded in Stash.", value=_safe_int(stats.get("total_play_count")))
        yield GaugeMetricFamily("stash_scenes_played_total", "Total number of scenes that have at least one recorded play.", value=_safe_int(stats.get("scenes_played")))

    def _collect_playtime_metrics(self, scenes: Iterable[Dict[str, Any]]) -> Iterable[GaugeMetricFamily]:
        """Collect play duration metrics bucketed by day of week and hour of day."""
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

            # Approximate per-play duration by evenly splitting across history entries
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

        # Yield day-of-week metrics
        dow_metric = GaugeMetricFamily(
            "stash_play_duration_seconds_by_dow",
            "Total play duration bucketed by day of week in seconds.",
            labels=["day_of_week"],
        )
        for dow_name, total_seconds in dow_totals.items():
            dow_metric.add_metric([dow_name], total_seconds)
        yield dow_metric

        # Yield hour-of-day metrics
        hour_metric = GaugeMetricFamily(
            "stash_play_duration_seconds_by_hour",
            "Total play duration bucketed by hour of day in seconds.",
            labels=["hour_of_day"],
        )
        for hour_key, total_seconds in hour_totals.items():
            hour_metric.add_metric([hour_key], total_seconds)
        yield hour_metric

    def _collect_metadata_metrics(self, scenes: Iterable[Dict[str, Any]]) -> Iterable[GaugeMetricFamily]:
        """Collect metadata/coverage metrics from scene data."""
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
                    marker_total += sum(1 for _ in markers)

        yield GaugeMetricFamily("stash_scenes_organized_total", "Total number of scenes marked as organized.", value=float(organized))
        yield GaugeMetricFamily("stash_scenes_with_stashid_total", "Total number of scenes that have at least one StashID entry.", value=float(with_stashid))
        yield GaugeMetricFamily("stash_scenes_tagged_total", "Total number of scenes that have at least one tag.", value=float(tagged))
        yield GaugeMetricFamily("stash_scenes_with_performers_total", "Total number of scenes that have at least one performer.", value=float(with_performers))
        yield GaugeMetricFamily("stash_scenes_with_studio_total", "Total number of scenes that have an associated studio.", value=float(with_studio))
        yield GaugeMetricFamily("stash_scenes_watched_total", "Total number of scenes that have at least one play.", value=float(watched))
        yield GaugeMetricFamily("stash_scenes_with_markers_total", "Total number of scenes that have at least one scene marker.", value=float(with_markers))
        yield GaugeMetricFamily("stash_scene_markers_total", "Total number of scene markers across all scenes.", value=float(marker_total))

    def _collect_tag_usage_metrics(self, scenes: Iterable[Dict[str, Any]]) -> Iterable[GaugeMetricFamily]:
        """Collect tag usage metrics from played scenes.

        Only the top 100 tags by usage count are exported to limit label cardinality.
        Using MetricFamily ensures stale tags are automatically cleared.
        """
        tag_usage_counts: Dict[str, int] = {}

        for scene in scenes:
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

        # Create metric with only current top 100 tags (stale tags automatically cleared)
        tag_metric = GaugeMetricFamily(
            "stash_tag_usage_count",
            "Number of played scenes using each tag. Only top 100 tags by usage are exported.",
            labels=["tag_name"],
        )
        for tag_name, count in top_tags:
            tag_metric.add_metric([tag_name], float(count))
        yield tag_metric

    def _collect_orgasm_metrics(self, scenes: Iterable[Dict[str, Any]]) -> Iterable[GaugeMetricFamily]:
        """Collect orgasm counter metrics per scene.

        Only scenes with o_counter > 0 are exported to limit cardinality.
        Using MetricFamily ensures stale scenes are automatically cleared.
        """
        orgasm_metric = GaugeMetricFamily(
            "stash_scene_o_counter",
            "Current orgasm counter value per scene (only scenes with o_counter > 0 are exported). Use increase() in PromQL to calculate new events over time windows.",
            labels=["scene_id"],
        )

        for scene in scenes:
            scene_id = str(scene.get("id", ""))
            if not scene_id:
                continue

            o_counter = _safe_int(scene.get("o_counter", 0))
            if o_counter > 0:
                orgasm_metric.add_metric([scene_id], float(o_counter))

        yield orgasm_metric

    def _collect_exporter_health_metrics(self, success: bool, duration: float) -> Iterable[GaugeMetricFamily]:
        """Collect exporter health and performance metrics."""
        yield GaugeMetricFamily("stash_up", "Whether the last scrape of Stash GraphQL succeeded (1 for success, 0 for failure).", value=1.0 if success else 0.0)
        yield GaugeMetricFamily("stash_scrape_duration_seconds", "Time spent on the last scrape in seconds.", value=duration)


__all__ = ["StashCollector"]

