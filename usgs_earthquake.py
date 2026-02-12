#!/usr/bin/env python3
"""
USGS Earthquake API Client

A Python client for interacting with the USGS Earthquake API
(https://earthquake.usgs.gov/fdsnws/event/1/).

Features:
- Filter earthquakes by time range (start_time, end_time)
- Filter by magnitude range (min_magnitude, max_magnitude)
- Filter by alert level (AlertLevel)
- Order results (OrderBy)

Example:
    from usgs_earthquake import UsgsClient, AlertLevel, OrderBy

    client = UsgsClient()
    result = (
        client.query()
        .start_time(2024, 1, 1, 0, 0)
        .end_time(2024, 12, 31, 23, 59)
        .min_magnitude(4.0)
        .alert_level(AlertLevel.GREEN)
        .order_by(OrderBy.TIME)
        .fetch()
    )

    print(f"Total earthquakes: {len(result['features'])}")
    for eq in result["features"]:
        props = eq["properties"]
        print(f"  {props['place']} - M{props['mag']}")
"""

from datetime import datetime, timezone
from enum import Enum

import requests


class AlertLevel(Enum):
    """USGS earthquake alert levels."""

    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"


class OrderBy(Enum):
    """Result ordering options."""

    TIME = "time"
    TIME_ASC = "time-asc"
    MAGNITUDE = "magnitude"
    MAGNITUDE_ASC = "magnitude-asc"


class UsgsApiError(Exception):
    """Raised when the USGS API returns an error."""


class UsgsQuery:
    """Query builder for the USGS Earthquake API.

    Allows filtering and customizing request parameters.
    Use :meth:`UsgsClient.query` to create a new instance.
    """

    _BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    def __init__(self, session: requests.Session):
        self._session = session
        self._start_time: datetime | None = None
        self._end_time: datetime = datetime.now(timezone.utc)
        self._min_magnitude: float = 0.0
        self._max_magnitude: float = 10.0
        self._alert_level: AlertLevel | None = None
        self._order_by: OrderBy = OrderBy.TIME

    # --- builder methods ---------------------------------------------------

    def start_time(self, year: int, month: int, day: int,
                   hour: int = 0, minute: int = 0) -> "UsgsQuery":
        """Set the start time for the query (UTC)."""
        self._start_time = datetime(year, month, day, hour, minute,
                                    tzinfo=timezone.utc)
        return self

    def end_time(self, year: int, month: int, day: int,
                 hour: int = 0, minute: int = 0) -> "UsgsQuery":
        """Set the end time for the query (UTC)."""
        self._end_time = datetime(year, month, day, hour, minute,
                                  tzinfo=timezone.utc)
        return self

    def min_magnitude(self, mag: float) -> "UsgsQuery":
        """Set the minimum magnitude filter."""
        self._min_magnitude = mag
        return self

    def max_magnitude(self, mag: float) -> "UsgsQuery":
        """Set the maximum magnitude filter."""
        self._max_magnitude = mag
        return self

    def alert_level(self, level: AlertLevel) -> "UsgsQuery":
        """Filter by alert level (green / yellow / orange / red)."""
        self._alert_level = level
        return self

    def order_by(self, order: OrderBy) -> "UsgsQuery":
        """Set result ordering."""
        self._order_by = order
        return self

    # --- execution ---------------------------------------------------------

    def _build_params(self) -> dict:
        """Build the query‑string parameters."""
        params: dict = {
            "format": "geojson",
            "endtime": self._end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "minmagnitude": str(self._min_magnitude),
            "maxmagnitude": str(self._max_magnitude),
            "orderby": self._order_by.value,
        }
        if self._start_time is not None:
            params["starttime"] = self._start_time.strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
        if self._alert_level is not None:
            params["alertlevel"] = self._alert_level.value
        return params

    def fetch(self) -> dict:
        """Execute the query and return the GeoJSON response as a *dict*.

        Raises:
            UsgsApiError: If the HTTP request fails.
        """
        params = self._build_params()
        try:
            response = self._session.get(
                self._BASE_URL, params=params, timeout=30
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise UsgsApiError(f"USGS API request failed: {exc}") from exc
        return response.json()


class UsgsClient:
    """Main USGS API client.

    Handles API requests and creates queries.
    """

    def __init__(self):
        self._session = requests.Session()

    def query(self) -> UsgsQuery:
        """Start a new :class:`UsgsQuery` with default parameters."""
        return UsgsQuery(self._session)


# ---------------------------------------------------------------------------
# Convenience CLI
# ---------------------------------------------------------------------------

def main():
    """Fetch recent significant earthquakes and print a summary."""
    client = UsgsClient()
    result = (
        client.query()
        .min_magnitude(4.5)
        .order_by(OrderBy.TIME)
        .fetch()
    )

    features = result.get("features", [])
    print(f"Total earthquakes (M≥4.5, last 30 days): {len(features)}\n")
    for eq in features[:20]:
        props = eq["properties"]
        mag = props.get("mag", "?")
        place = props.get("place", "Unknown")
        time_ms = props.get("time")
        time_str = (
            datetime.fromtimestamp(time_ms / 1000, tz=timezone.utc).strftime(
                "%Y-%m-%d %H:%M UTC"
            )
            if time_ms
            else "?"
        )
        print(f"  M{mag:<5}  {time_str}  {place}")

    if len(features) > 20:
        print(f"\n  ... and {len(features) - 20} more")


if __name__ == "__main__":
    main()
