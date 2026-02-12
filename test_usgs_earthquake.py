#!/usr/bin/env python3
"""Tests for the USGS Earthquake API client."""

import json
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from usgs_earthquake import (
    AlertLevel,
    OrderBy,
    UsgsApiError,
    UsgsClient,
    UsgsQuery,
)

# A minimal GeoJSON response fixture
_SAMPLE_RESPONSE = {
    "type": "FeatureCollection",
    "metadata": {"generated": 1700000000000, "count": 1},
    "features": [
        {
            "type": "Feature",
            "properties": {
                "mag": 5.2,
                "place": "10 km NE of Hualien, Taiwan",
                "time": 1700000000000,
                "alert": "green",
                "type": "earthquake",
            },
            "geometry": {
                "type": "Point",
                "coordinates": [121.65, 24.05, 10.0],
            },
        }
    ],
}


class TestAlertLevel(unittest.TestCase):
    def test_values(self):
        self.assertEqual(AlertLevel.GREEN.value, "green")
        self.assertEqual(AlertLevel.YELLOW.value, "yellow")
        self.assertEqual(AlertLevel.ORANGE.value, "orange")
        self.assertEqual(AlertLevel.RED.value, "red")


class TestOrderBy(unittest.TestCase):
    def test_values(self):
        self.assertEqual(OrderBy.TIME.value, "time")
        self.assertEqual(OrderBy.TIME_ASC.value, "time-asc")
        self.assertEqual(OrderBy.MAGNITUDE.value, "magnitude")
        self.assertEqual(OrderBy.MAGNITUDE_ASC.value, "magnitude-asc")


class TestUsgsQueryBuildParams(unittest.TestCase):
    """Test that the query builder produces correct API parameters."""

    def setUp(self):
        self.client = UsgsClient()

    def test_default_params(self):
        query = self.client.query()
        params = query._build_params()
        self.assertEqual(params["format"], "geojson")
        self.assertEqual(params["minmagnitude"], "0.0")
        self.assertEqual(params["maxmagnitude"], "10.0")
        self.assertEqual(params["orderby"], "time")
        self.assertNotIn("starttime", params)
        self.assertNotIn("alertlevel", params)

    def test_start_and_end_time(self):
        query = (
            self.client.query()
            .start_time(2024, 1, 15, 8, 30)
            .end_time(2024, 6, 30, 23, 59)
        )
        params = query._build_params()
        self.assertEqual(params["starttime"], "2024-01-15T08:30:00")
        self.assertEqual(params["endtime"], "2024-06-30T23:59:00")

    def test_magnitude_filter(self):
        query = self.client.query().min_magnitude(3.0).max_magnitude(7.5)
        params = query._build_params()
        self.assertEqual(params["minmagnitude"], "3.0")
        self.assertEqual(params["maxmagnitude"], "7.5")

    def test_alert_level(self):
        query = self.client.query().alert_level(AlertLevel.ORANGE)
        params = query._build_params()
        self.assertEqual(params["alertlevel"], "orange")

    def test_order_by(self):
        query = self.client.query().order_by(OrderBy.MAGNITUDE_ASC)
        params = query._build_params()
        self.assertEqual(params["orderby"], "magnitude-asc")

    def test_chained_builder(self):
        query = (
            self.client.query()
            .start_time(2024, 1, 1, 0, 0)
            .end_time(2024, 12, 31, 23, 59)
            .min_magnitude(4.0)
            .max_magnitude(8.0)
            .alert_level(AlertLevel.GREEN)
            .order_by(OrderBy.TIME_ASC)
        )
        params = query._build_params()
        self.assertEqual(params["starttime"], "2024-01-01T00:00:00")
        self.assertEqual(params["endtime"], "2024-12-31T23:59:00")
        self.assertEqual(params["minmagnitude"], "4.0")
        self.assertEqual(params["maxmagnitude"], "8.0")
        self.assertEqual(params["alertlevel"], "green")
        self.assertEqual(params["orderby"], "time-asc")


class TestUsgsQueryFetch(unittest.TestCase):
    """Test HTTP interactions using mocked requests."""

    @patch("usgs_earthquake.requests.Session")
    def test_fetch_success(self, MockSession):
        mock_response = MagicMock()
        mock_response.json.return_value = _SAMPLE_RESPONSE
        mock_response.raise_for_status = MagicMock()
        mock_session = MockSession.return_value
        mock_session.get.return_value = mock_response

        client = UsgsClient()
        client._session = mock_session

        result = client.query().min_magnitude(4.0).fetch()

        mock_session.get.assert_called_once()
        self.assertEqual(len(result["features"]), 1)
        self.assertEqual(result["features"][0]["properties"]["mag"], 5.2)

    @patch("usgs_earthquake.requests.Session")
    def test_fetch_http_error(self, MockSession):
        import requests as _requests
        mock_session = MockSession.return_value
        mock_session.get.side_effect = _requests.ConnectionError("connection error")

        client = UsgsClient()
        client._session = mock_session

        with self.assertRaises(UsgsApiError):
            client.query().fetch()


if __name__ == "__main__":
    unittest.main()
