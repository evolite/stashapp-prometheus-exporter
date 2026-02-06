"""
Thin HTTP client for the Stash GraphQL API.

This module intentionally keeps only the minimal logic needed by the exporter:
posting a GraphQL query with an API key header and basic error handling.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

LOG = logging.getLogger(__name__)


class StashClientError(Exception):
    """Raised when a call to the Stash GraphQL API fails."""


@dataclass
class StashClient:
    """Simple Stash GraphQL client."""

    base_url: str
    api_key: str | None
    timeout_seconds: int = 10

    def run_query(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a GraphQL query and return the `data` dictionary.

        Raises StashClientError on network errors, non‑200 responses or GraphQL errors.
        """

        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["ApiKey"] = self.api_key
        payload: Dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=self.timeout_seconds,
            )
        except requests.RequestException as exc:
            raise StashClientError(
                f"Error connecting to Stash GraphQL at {self.base_url}: {exc}"
            ) from exc

        if response.status_code != 200:
            raise StashClientError(
                f"Unexpected status code {response.status_code} from Stash GraphQL: {response.text}"
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise StashClientError("Invalid JSON received from Stash GraphQL") from exc

        errors = payload.get("errors")
        if errors:
            raise StashClientError(f"GraphQL errors returned from Stash: {errors}")

        if "data" not in payload:
            raise StashClientError("GraphQL response missing 'data' field")

        return payload["data"]


__all__ = ["StashClient", "StashClientError"]
