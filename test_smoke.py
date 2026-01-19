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
    import pygmt  # noqa: F401

    # Local module import
    import eewrep_function  # noqa: F401

    # Data files
    check_file("station.txt")
    check_file("county_list.txt")
    check_file("city_2016.gmt")

    rep_files = glob.glob(os.path.join("192", "*.rep"))
    if not rep_files:
        raise FileNotFoundError("No .rep files found in 192/")

    print("Smoke test OK")
    print(f"rep files: {len(rep_files)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
