"""
Entrypoint for the StashApp Prometheus exporter.

This process periodically queries the Stash GraphQL API for aggregate
library statistics and exposes them as Prometheus metrics on /metrics.
"""

from __future__ import annotations

import logging
import signal
import sys
import time
from typing import Any, Dict

from prometheus_client import start_http_server

from .config import Config, configure_logging, load_config
from .metrics import (
    stash_up,
    update_metadata_from_scenes,
    update_metrics_from_stats,
    update_playtime_buckets_from_scenes,
)
from .queries import LIBRARY_STATS_QUERY, SCENE_PLAY_HISTORY_QUERY
from .stash_client import StashClient, StashClientError


LOG = logging.getLogger(__name__)
_SHOULD_STOP = False


def _handle_signal(signum: int, frame: Any) -> None:  # type: ignore[override]
    global _SHOULD_STOP
    LOG.info("Received signal %s, shutting down gracefully", signum)
    _SHOULD_STOP = True


def _install_signal_handlers() -> None:
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _handle_signal)
        except ValueError:
            # Signals may not be available or usable in some environments
            continue


def _scrape_once(client: StashClient) -> None:
    """Execute a single scrape from Stash and update Prometheus metrics."""

    try:
        data: Dict[str, Any] = client.run_query(LIBRARY_STATS_QUERY)
        stats = data.get("stats") or {}
        update_metrics_from_stats(stats)

        # Derive playtime buckets and metadata coverage from scene data.
        scenes_data: Dict[str, Any] = client.run_query(SCENE_PLAY_HISTORY_QUERY)
        scenes_root = scenes_data.get("findScenes") or {}
        scenes = scenes_root.get("scenes") or []
        update_playtime_buckets_from_scenes(scenes)
        update_metadata_from_scenes(scenes)

        stash_up.set(1.0)
    except StashClientError as exc:
        LOG.error("Failed to scrape Stash GraphQL: %s", exc)
        # Keep last known values for other metrics, but mark exporter as down.
        stash_up.set(0.0)


def _scrape_loop(client: StashClient, config: Config) -> None:
    """Background loop that periodically scrapes Stash."""

    global _SHOULD_STOP
    interval = config.scrape_interval_seconds
    LOG.info("Starting scrape loop with interval %s seconds", interval)

    while not _SHOULD_STOP:
        start = time.monotonic()
        _scrape_once(client)
        elapsed = time.monotonic() - start

        # Sleep the remainder of the interval, but never negative.
        sleep_for = max(0.0, interval - elapsed)
        if _SHOULD_STOP:
            break
        time.sleep(sleep_for)

    LOG.info("Scrape loop stopped")


def main() -> int:
    try:
        config = load_config()
    except Exception as exc:
        # Logging may not yet be configured; print to stderr as last resort.
        print(f"Failed to load configuration: {exc}", file=sys.stderr)
        return 1

    configure_logging(config.log_level)

    LOG.info("Starting StashApp Prometheus exporter")
    LOG.debug("Using Stash GraphQL URL: %s", config.stash_graphql_url)

    client = StashClient(base_url=config.stash_graphql_url, api_key=config.stash_api_key)

    # Expose /metrics before starting the scrape loop so Prometheus can connect.
    start_http_server(config.exporter_listen_port)
    LOG.info("Prometheus metrics server listening on :%s", config.exporter_listen_port)

    _install_signal_handlers()

    try:
        _scrape_loop(client, config)
    except KeyboardInterrupt:
        LOG.info("KeyboardInterrupt received, exiting")

    LOG.info("Exporter stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

