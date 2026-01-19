#!/bin/python
from datetime import datetime, timedelta
from typing import Optional
import argparse
import os
import re
import glob

BASE_FOLDER = globals().get("FOLDER", r"./192")
OUTPUT_PATH = globals().get("SUMMARY_PATH", "./outputs/summary_20_192.txt")
rep_files = []

_outdir = os.path.dirname(OUTPUT_PATH)
if _outdir and not os.path.exists(_outdir):
    os.makedirs(_outdir, exist_ok=True)
    print("Make New File")


def unpackPfile(infile: str) -> dict:
    with open(infile) as f:
        lines = f.readlines()

    tmp = lines[0]
    year = int(tmp[1:5])
    month = int(tmp[5:7])
    day = int(tmp[7:9])
    hour = int(tmp[9:11])
    minute = int(tmp[11:13])
    sec = float(tmp[13:19])

    dt = datetime(year, month, day, hour, minute, int(sec // 1), int(sec % 1 * 1000000))
    mag = float(tmp[40:44])

    pfile_info = {}
    pfile_info["ori_time"] = dt
    pfile_info["mag"] = mag

    intensity = {}
    arrival_time = {}
    weighting = {}
    pga = {}
    for i in lines[1:]:
        sta = i[:5].strip()  # strip 去掉左右空格
        weighting[sta] = int(float(i[35:39]))
        if i[76:77] == " ":
            intensity[sta] = int(0)
        else:
            intensity[sta] = int(i[76:77])
        pga[sta] = float(i[78:83])
        arrival_time[sta] = pfile_info["ori_time"].replace(
            minute=int(i[21:23]), second=0, microsecond=0
        ) + timedelta(seconds=float(i[23:29]))
    pfile_info["intensity"] = intensity
    pfile_info["arrival_time"] = arrival_time
    pfile_info["weighting"] = weighting
    pfile_info["pga"] = pga

    return pfile_info


# === ERR event info ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert .rep files to summary output (Pfile input)"
    )
    parser.add_argument(
        "pfile",
        help="要讀取的 Pfile 檔名，例如 17010623.P20"
    )
    parser.add_argument(
        "--base-folder",
        default=BASE_FOLDER,
        help="rep 檔案所在目錄（預設 ./192）"
    )
    args = parser.parse_args()

    BASE_FOLDER = args.base_folder
    rep_files = glob.glob(os.path.join(BASE_FOLDER, "*.rep"), recursive=True)
    basefolder_name = os.path.basename(os.path.normpath(BASE_FOLDER))
    pfilename = os.path.splitext(os.path.basename(args.pfile))[0]
    OUTPUT_PATH = f"./outputs/summary_{basefolder_name}_{pfilename}.txt"

    _outdir = os.path.dirname(OUTPUT_PATH)
    if _outdir and not os.path.exists(_outdir):
        os.makedirs(_outdir, exist_ok=True)

    pfile_info = unpackPfile(args.pfile)
    if not pfile_info:
        raise FileNotFoundError("找不到對應的 Pfile 檔案")

    ref_lat = None
    ref_lon = None
    ref_dep = None
    ref_mag = pfile_info["mag"]
    ref_time = pfile_info["ori_time"]

    print(">> 成功讀取時間、規模 (Pfile)")


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
    header1 = header_fmt.format("Mag", "Lat", "Lon", "Depth", "Or.", "Ma.", "Repfile", "Report_time", "note")
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
        if i == last_idx and i != 0:  # 確保若只有一筆時不會同時出現 first/final
            notes.append("(final) ")

        # D. 處理原本 rep_file 內可能帶有的標籤 (eew/pws)
        # 如果 process_rep_file 已經把 note 放在 row 裡了，這裡要拆出來
        # 這裡假設原本的 line 只有 8 欄，我們在末端補上組合後的 note
        note_str = "".join(notes)

        # 格式化輸出：原有的 line 加上新生成的 note_str
        fout.write(f"{line} {note_str:>10}\n")

print(f" Final summary：{OUTPUT_PATH}")
