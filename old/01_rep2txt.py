#!/bin/python
from datetime import datetime
from typing import Optional
import argparse
import eewrep_function
import os
import re
import glob

BASE_FOLDER = globals().get("FOLDER", r"./192")
OUTPUT_PATH = globals().get("SUMMARY_PATH", "./outputs/summary_20_192.txt")
rep_files = glob.glob(os.path.join("./192/", "*.rep"), recursive=True)

_outdir = os.path.dirname(OUTPUT_PATH)
if _outdir and not os.path.exists(_outdir):
    os.makedirs(_outdir, exist_ok=True)
    print("Make New File")

# === ERR event info ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert .rep files to summary output"
    )
    parser.add_argument(
        "eq_id",
        help="地震年份(西元)+編號，例如 2025001"
    )
    args = parser.parse_args()

    eq_info = None
    lines = []

    eq_input = args.eq_id.strip()
    year = eq_input[:4]
    eq_id = eq_input[4:].zfill(3)

    eq_info = eewrep_function.read_eq_xml(year, eq_id)
    if not eq_info:
        raise FileNotFoundError("not found XML")

    if eq_info:
        print(">> Successfully read time, location, and magnitude")
        report = eq_info["reportContent"]

        m = re.match(r"(\d{2})/(\d{2})-\d{2}:\d{2}(.*)magnitude ([\d.]+) felt EQ", report)
        if m:
            month, day, location, magnitude = m.groups()
            roc_year = int(year) - 1911
            lines = [
                f"{roc_year}年{int(month)}月{int(day)}日",
                f"{location}  規模{magnitude}地震"
            ]
        else:
            # 若格式不符合，直接放整行文字
            print("format not match")
            lines = [report]

ref_lat, ref_lon = eq_info["epicenterLat"], eq_info["epicenterLon"]
ref_mag, ref_dep = eq_info["magnitude"], eq_info["depth"]
ref_time = eq_info["ot"]

# === time to UTC ===
# < IF Python >= 3.10 ## >
# REPORT_RE = re.compile(r"Reporting time\s+(\d{4}/\d{2}/\d{2})\s+(\d{2}:\d{2}:\d{2}(?:\.\d+)?)")
# def parse_reporting_time(text_line: str) -> datetime | None:
#    m = REPORT_RE.search(text_line)
#    if not m:
#        return None
#    date_s, time_s = m.group(1), m.group(2)
#    if "." in time_s:
#        return datetime.strptime(f"{date_s} {time_s}", "%Y/%m/%d %H:%M:%S.%f")
#    return datetime.strptime(f"{date_s} {time_s}.000000", "%Y/%m/%d %H:%M:%S.%f")

# < Python = 3.7 >
REPORT_RE = re.compile(r"Reporting\s+time\s+(\d{4}/\d{2}/\d{2})\s+(\d{2}:\d{2}:\d{2}(?:\.\d+)?)")
def parse_reporting_time(text_line: str) -> Optional[datetime]:
    m = REPORT_RE.search(text_line)
    if not m:
        return None
    date_s, time_s = m.group(1), m.group(2)
    
    full_time_s = f"{date_s} {time_s}"
    if "." in time_s:
        return datetime.strptime(full_time_s, "%Y/%m/%d %H:%M:%S.%f")
    return datetime.strptime(full_time_s, "%Y/%m/%d %H:%M:%S")

# === REP soloutions info ===
def looks_like_station_row(s: str) -> bool:
    return bool(re.match(r"^\s*[A-Za-z0-9]", s))

def process_rep_file(rep_path: str) -> str:
    with open(rep_path, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()
    lines = [ln.strip() for ln in raw_lines if ln.strip()]

    if len(lines) < 3:
        raise ValueError("NOT ENOUGH DATA")

    # === Reporting time：===
    reporting_time = None
    for ln in raw_lines:
        reporting_time = parse_reporting_time(ln)
        if reporting_time:
            break
    if not reporting_time:
        raise ValueError("CANT FIND Reporting time")

    # === 取 lat / lon / depth / mpd ===
    lat = lon = depth = mpd = ""
    for ln in lines:
        p = ln.split()
        if len(p) >= 13 and p[0].replace(".", "", 1).isdigit():
            try:
                lat, lon, depth, mpd = p[6], p[7], p[8], p[12]
                break
            except Exception:
                continue
    if not (lat and lon and depth and mpd):
        raise ValueError("CANT FIND MAINSHOCK IMFO（lat/lon/depth/mpd）")

    # = Stations： =
    station_count = 0
    header_idx = -1
    for i, ln in enumerate(raw_lines):
        s = ln.strip()
        if s.startswith("Sta") or s.startswith("Station") or s.startswith("#St."):
            header_idx = i
            break
    if header_idx >= 0:
        for ln in raw_lines[header_idx + 1:]:
            s = ln.strip()
            if not s:
                break
            if re.match(r"^-{3,}$", s):
                break
            if looks_like_station_row(s):
                station_count += 1
            else:
                break

    # = Author =
    author_id = os.path.splitext(os.path.basename(rep_path))[0]

    # = outputs =
    row = "{:>5.2f} {:>9.4f} {:>10.4f} {:>7.2f} {:>4} {:>4} {:>30} {:>26}".format(
        float(mpd),
        float(lat),
        float(lon),
        float(depth),
        station_count,
        station_count,
        author_id,
        reporting_time.strftime("%Y/%m/%d-%H:%M:%S.%f")
    )
    return row

# === Only a P-FILE get Origin Time === 
# with open ("./13201617.P25", "r", encoding = "utf-8") as f:
#    lines = f.readlines()
#    header = lines[0]
#    
#    y, m, d = int(header[0:5]), int(header[5:7]), int(header[7:9])
#    H, M = int(header[9:11]), int(header[11:13])
#    S = float(header[13:19])
#    origin_time = datetime(y, m, d, H, M, int(S), int((S - int(S)) * 1_000_000))
#    origin_time_str = origin_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4]


# === Final Output ===
rows = []
for rep_file in rep_files:
    try:
        row = process_rep_file(rep_file)
        rows.append(row)
    except Exception as e:
        print(f"Skip {rep_file} {e}")
lines_sorted = sorted(rows, key=lambda x: ((x.strip().split()[7]), x.strip().split()[6]))

# --- 1. 找出最大規模 (max_mag) 的索引 ---
max_mag = -1.0
max_idx = -1

# 先解析一遍找出最大值的位置
for i, line in enumerate(lines_sorted):
    parts = line.strip().split()
    mag = float(parts[0])
    if mag > max_mag:
        max_mag = mag
        max_idx = i

with open(OUTPUT_PATH, "w", encoding="utf-8") as fout:
    header_fmt = ("{:>5} {:>9} {:>10} {:>7} {:>4} {:>4} {:>30} {:>26} {:>10}")
    header1 = header_fmt.format("Mag","Lat","Lon","Depth","Or.","Ma.","Repfile","Report_time", "note")
    fout.write(header1 + "\n")

    last_idx = len(lines_sorted) - 1

    for i, line in enumerate(lines_sorted):
        notes = []
        
        # A. 標記最初解 (first)
        if i == 0:
            notes.append("(first)")
        
        # B. 標記最大規模解 (max_mag)
        if i == max_idx:
            notes.append("(max_mag)")
            
        # C. 標記最終解 (final)
        if i == last_idx and i != 0: # 確保若只有一筆時不會同時出現 first/final
            notes.append("(final) ")

        # D. 處理原本 rep_file 內可能帶有的標籤 (eew/pws)
        # 如果 process_rep_file 已經把 note 放在 row 裡了，這裡要拆出來
        # 這裡假設原本的 line 只有 8 欄，我們在末端補上組合後的 note
        note_str = "".join(notes)
        
        # 格式化輸出：原有的 line 加上新生成的 note_str
        fout.write(f"{line} {note_str:>10}\n")

    # for line in lines_sorted:
        # fout.write(line + "\n")

print(f" Final summary：{OUTPUT_PATH}")
