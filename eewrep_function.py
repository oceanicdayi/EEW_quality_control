# ----- Cauculate lon/lat Error ----------------------------------------------------------

from obspy.geodetics import gps2dist_azimuth

def cal_horizontal_error(lat, lon, ref_lat, ref_lon):
    dist_m, _, _ = gps2dist_azimuth(lat, lon, ref_lat, ref_lon)
    return dist_m / 1000

# ----- ERR event info by .xml -----------------------------------------------------------

import os
import re
import sys
from glob import glob
# python 3.7 #
from datetime import datetime, timezone
from typing import Optional
###
import numpy as np
import xml.etree.ElementTree as ET

#img_folder = r"/home/sysop/EEW"
#img_folder2 = r"/home/sysop/EEW/output"

img_folder = r"D:\WORK\eew_quality"
img_folder2 = r"D:\WORK\eew_quality\output"

def parse_origin_time(time_str: str) -> Optional[datetime]:
    """
    將 XML 中的時間字串轉為 UTC datetime
    """
    if not time_str:
        return None

    dt = datetime.fromisoformat(time_str)  # 支援 +08:00（Python 3.7 OK）
    return dt.astimezone(timezone.utc)

def read_eq_xml(year, eq_id, base_dir= img_folder):
    """
    year: 西元年份 (str)，例如 '2025'
    eq_id: 地震編號 (str, 例如 '001')
    base_dir: 存放 xml 檔的資料夾
    """
    eq_id = eq_id.zfill(3)  # 確保是三位數
    roc_year = int(year) - 1911  # 轉民國年 (2025 → 114)

    # 檔案格式：CWA-EQ114001-2025-0102-010203.xml
    pattern = os.path.join(base_dir, f"CWA-EQ{roc_year}{eq_id}-{year}-*.xml")
    files = glob(pattern)

    if not files:
        print(f"找不到檔案: {pattern}")
        return None

    filepath = files[0]
    print(f"讀取檔案: {os.path.basename(filepath)}")

    # 解析 XML
    tree = ET.parse(filepath)
    root = tree.getroot()
    ns = {"xmlns":"urn:cwa:gov:tw:cwacommon:0.1"}
    # report = root.findtext(".//xmlns:reportContent", namespaces=ns)
    origin_time_str = root.findtext(".//xmlns:originTime", namespaces=ns)
    origin_time_utc = parse_origin_time(origin_time_str)

    eq_data = {
        "ot": origin_time_utc,
        "magnitude": float(root.findtext(".//xmlns:magnitudeValue", namespaces=ns)),
        "epicenterLon": float(root.findtext(".//xmlns:epicenterLon", namespaces=ns)),
        "epicenterLat": float(root.findtext(".//xmlns:epicenterLat", namespaces=ns)),
        "depth": float(root.findtext(".//xmlns:depth", namespaces=ns)),
        "reportContent": root.findtext(".//xmlns:reportContent", namespaces=ns)
    }

    return eq_data

# ----- Cauculate lon/lat Error ----------------------------------------------------------
