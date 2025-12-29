"""
Entrypoint for the StashApp Prometheus exporter.

This exporter follows Prometheus best practices by using synchronous scraping:
metrics are only collected when Prometheus requests them via /metrics, not on a timer.

All metrics are collected using a custom Collector pattern, which ensures:
- Synchronous scraping (only when Prometheus requests metrics)
- No stale labels (MetricFamily objects create metrics fresh each scrape)
- Fully stateless operation (no cached data between scrapes)
"""

from __future__ import annotations

import logging
import signal
import sys

from prometheus_client import REGISTRY, start_http_server

from .collector import StashCollector
from .config import Config, configure_logging, load_config
from .stash_client import StashClient


LOG = logging.getLogger(__name__)
_SHOULD_STOP = False


def _handle_signal(signum: int, frame: object) -> None:
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


def main() -> int:
    try:
        config = load_config()
    except Exception as exc:
        # Logging may not yet be configured; print to stderr as last resort.
        print(f"Failed to load configuration: {exc}", file=sys.stderr)
        return 1

    configure_logging(config.log_level)

    LOG.info("Starting StashApp Prometheus exporter (synchronous scraping)")
    LOG.debug("Using Stash GraphQL URL: %s", config.stash_graphql_url)

    client = StashClient(base_url=config.stash_graphql_url, api_key=config.stash_api_key)

    # Register the custom collector for synchronous scraping
    # The collector will be called by Prometheus on each /metrics request
    collector = StashCollector(client)
    REGISTRY.register(collector)
    LOG.info("Registered StashCollector for synchronous metric collection")

    # Start HTTP server - scraping happens when Prometheus requests /metrics
    start_http_server(config.exporter_listen_port)
    LOG.info("Prometheus metrics server listening on :%s", config.exporter_listen_port)
    LOG.info("Metrics will be collected synchronously when Prometheus scrapes /metrics")

    _install_signal_handlers()

    # Keep the process running - scraping happens on-demand when Prometheus requests metrics
    try:
        while not _SHOULD_STOP:
            # Use signal.pause() on Unix, or sleep on Windows
            try:
                signal.pause()  # Wait for signals (Unix only)
            except AttributeError:
                # Windows doesn't have signal.pause(), use sleep instead
                import time
                time.sleep(1)
    except KeyboardInterrupt:
        LOG.info("KeyboardInterrupt received, exiting")

    LOG.info("Exporter stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

