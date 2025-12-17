"""
Configuration loading for the StashApp Prometheus exporter.

Environment variables:
    STASH_GRAPHQL_URL       – Stash GraphQL endpoint
                              (default: http://stash:9999/graphql)
    STASH_API_KEY           – Stash API key (required)
    SCRAPE_INTERVAL_SECONDS – Interval between Stash scrapes (default: 30)
    EXPORTER_LISTEN_PORT    – Port for /metrics HTTP server (default: 9100)
    LOG_LEVEL               – Python log level name (default: INFO)
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import os


@dataclass(frozen=True)
class Config:
    """Runtime configuration for the exporter."""

    stash_graphql_url: str
    stash_api_key: str
    scrape_interval_seconds: int
    exporter_listen_port: int
    log_level: str


def _get_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"Invalid integer value for {name}: {raw!r}") from exc


def load_config() -> Config:
    """Load configuration from environment variables."""

    url = os.getenv("STASH_GRAPHQL_URL", "http://stash:9999/graphql").rstrip("/")
    api_key = os.getenv("STASH_API_KEY")
    if not api_key:
        raise RuntimeError("STASH_API_KEY environment variable is required")

    scrape_interval = _get_env_int("SCRAPE_INTERVAL_SECONDS", 30)
    if scrape_interval <= 0:
        raise ValueError("SCRAPE_INTERVAL_SECONDS must be positive")

    listen_port = _get_env_int("EXPORTER_LISTEN_PORT", 9100)
    if not (1 <= listen_port <= 65535):
        raise ValueError("EXPORTER_LISTEN_PORT must be between 1 and 65535")

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    return Config(
        stash_graphql_url=url,
        stash_api_key=api_key,
        scrape_interval_seconds=scrape_interval,
        exporter_listen_port=listen_port,
        log_level=log_level,
    )


def configure_logging(log_level: str) -> None:
    """Configure root logger according to LOG_LEVEL."""

    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


