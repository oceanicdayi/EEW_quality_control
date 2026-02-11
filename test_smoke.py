from __future__ import annotations

import glob
import os
import sys


def check_file(path: str) -> None:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Missing required file: {path}")


def main() -> int:
    # Import checks
    import pandas as pd  # noqa: F401
    import matplotlib.pyplot as plt  # noqa: F401
    import numpy as np  # noqa: F401
    import obspy  # noqa: F401
    
    # PyGMT requires GMT system library, make it optional
    try:
        import pygmt  # noqa: F401
        print("✓ pygmt available")
    except Exception as e:
        print(f"⚠ pygmt not fully available (requires GMT system library): {e}")
        print("  Note: Some plotting scripts may not work without GMT installed")

    # Local module import
    import eewrep_function  # noqa: F401

    # Data files (optional - not present in all deployment environments)
    print("\n=== Checking optional data files ===")
    data_files = ["station.txt", "county_list.txt", "city_2016.gmt"]
    for filepath in data_files:
        if os.path.isfile(filepath):
            print(f"✓ {filepath} found")
        else:
            print(f"⚠ {filepath} not found (optional)")

    # Check for .rep files in 192 directory
    if os.path.isdir("192"):
        rep_files = glob.glob(os.path.join("192", "*.rep"))
        if rep_files:
            print(f"✓ Found {len(rep_files)} .rep files in 192/")
        else:
            print("⚠ No .rep files found in 192/ (optional)")
    else:
        print("⚠ 192/ directory not found (optional)")

    print("\n✓ Smoke test passed - all required modules available")
    return 0


if __name__ == "__main__":
    sys.exit(main())
