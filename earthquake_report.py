#!/usr/bin/env python3
"""
Earthquake Report Generator

Runs the USGS earthquake query, formats the results into a readable report,
and saves it to a file for email delivery via GitHub Actions.
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from usgs_earthquake import OrderBy, UsgsClient

MAX_DISPLAY = 50


def fetch_earthquakes():
    """Fetch recent significant earthquakes from the USGS API."""
    client = UsgsClient()
    result = (
        client.query()
        .min_magnitude(4.5)
        .order_by(OrderBy.TIME)
        .fetch()
    )
    return result


def format_report(result):
    """Format earthquake data into a readable report string."""
    features = result.get("features", [])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    repository = os.getenv("GITHUB_REPOSITORY", "oceanicdayi/EEW_quality_control")
    run_id = os.getenv("GITHUB_RUN_ID", "N/A")
    run_number = os.getenv("GITHUB_RUN_NUMBER", "N/A")

    lines = []
    lines.append("=" * 70)
    lines.append("  USGS Earthquake Report (M >= 4.5, last 30 days)")
    lines.append("=" * 70)
    lines.append(f"  Generated: {now}")
    lines.append(f"  Total earthquakes found: {len(features)}")
    lines.append(f"  Workflow run: #{run_number} (ID: {run_id})")
    lines.append("-" * 70)
    lines.append("")

    if not features:
        lines.append("  No earthquakes found matching the criteria.")
    else:
        lines.append(f"  {'Mag':<8}{'Time (UTC)':<22}{'Location'}")
        lines.append(f"  {'---':<8}{'----------':<22}{'--------'}")
        for eq in features[:MAX_DISPLAY]:
            props = eq["properties"]
            mag = props.get("mag", "?")
            place = props.get("place", "Unknown")
            time_ms = props.get("time")
            if time_ms:
                time_str = datetime.fromtimestamp(
                    time_ms / 1000, tz=timezone.utc
                ).strftime("%Y-%m-%d %H:%M")
            else:
                time_str = "?"
            lines.append(f"  M{mag:<7}{time_str:<22}{place}")

        if len(features) > MAX_DISPLAY:
            lines.append(f"\n  ... and {len(features) - MAX_DISPLAY} more earthquakes")

    lines.append("")
    lines.append("-" * 70)
    lines.append("  Data source: USGS Earthquake Hazards Program")
    lines.append("  API: https://earthquake.usgs.gov/fdsnws/event/1/")
    lines.append(f"  Repository: https://github.com/{repository}")
    if run_id != "N/A":
        lines.append(
            f"  Run details: https://github.com/{repository}/actions/runs/{run_id}"
        )
    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    """Fetch earthquakes, generate report, and save to file."""
    print("Fetching earthquake data from USGS API...")

    try:
        result = fetch_earthquakes()
    except Exception as exc:
        print(f"Error fetching earthquake data: {exc}", file=sys.stderr)
        return 1

    report = format_report(result)
    print(report)

    output_path = Path("earthquake_report.txt")
    output_path.write_text(report, encoding="utf-8")
    print(f"\nReport saved to: {output_path.absolute()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
