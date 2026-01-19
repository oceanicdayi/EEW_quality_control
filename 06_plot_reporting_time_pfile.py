#!/bin/python
import argparse
import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import eewrep_function
import numpy as np
import re


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
        description="Plot EEW reporting time (Pfile input)"
    )
    parser.add_argument(
        "pfile",
        help="要讀取的 Pfile 檔名，例如 17010623.P20"
    )
    parser.add_argument(
        "--base-folder",
        default="./192",
        help="rep 檔案所在目錄（預設 ./192）"
    )
    args = parser.parse_args()

    pfile_info = unpackPfile(args.pfile)
    if not pfile_info:
        raise FileNotFoundError("找不到對應的 Pfile 檔案")

    ref_lat = None
    ref_lon = None
    ref_dep = None
    ref_mag = pfile_info["mag"]
    # Treat Pfile origin time as UTC to match Report_time (UTC)
    ref_time = pd.Timestamp(pfile_info["ori_time"], tz="UTC")

    print(">> 成功讀取時間、規模 (Pfile)")

# === EEW rep ===
basefolder_name = os.path.basename(os.path.normpath(args.base_folder))
pfilename = os.path.splitext(os.path.basename(args.pfile))[0]
INPUT_PATH = f"./outputs/summary_{basefolder_name}_{pfilename}.txt"
df = pd.read_csv(INPUT_PATH, sep=r"\s+")
for col in ["Mag", "Lat", "Lon", "Depth", "Ma."]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

if "Report_time" not in df.columns and "Date" in df.columns and "Time" in df.columns:
    df["Report_time"] = df["Date"].str.replace("-", "") + " " + df["Time"]

# Parse times as UTC to match ref_time
df["Tdiff"] = pd.to_datetime(df["Report_time"], errors="coerce", utc=True) - ref_time
df["Tdiff_second"] = df["Tdiff"].dt.total_seconds()
print(df["Tdiff"])

df["Repfile_short"] = df["Repfile"].apply(lambda x: "_".join(x.split("_")[-2:]))

# === Proessing time histogram ===
fig, ax = plt.subplots(figsize=(14, 7))

colors = []
for note in df["note"]:
    if "(eew)" in str(note).lower():
        colors.append("green")
    elif "(pws)" in str(note).lower():
        colors.append("orange")
    elif str(note) != "nan":
        colors.append("red")
    else:
        colors.append("skyblue")

bars = ax.bar(df["Repfile_short"], df["Tdiff_second"], color=colors, edgecolor="black", linewidth=0.5)

y_vals = df["Tdiff_second"].dropna()
if y_vals.empty:
    y_min, y_max = 0, 1
else:
    y_min, y_max = y_vals.min(), y_vals.max()
annot_count = 0

# --- Annotations ---
for bar, note, mag in zip(bars, df["note"], df["Mag"]):
    is_valid_note = not pd.isna(note) and str(note).strip() != ""

    if is_valid_note:
        yval = bar.get_height()
        label = f"M{mag:.2f}\n{note}"

        note_lower = str(note).lower()
        if "(eew)" in note_lower:
            theme_color = "green"
        elif "(pws)" in note_lower:
            theme_color = "darkorange"
        else:
            theme_color = "red"

        offsets = [100, 150, 40, 200]
        offset_y = offsets[annot_count % 4]
        annot_count += 1

        ax.annotate(
            label,
            xy=(bar.get_x() + bar.get_width() / 2, yval),
            xytext=(0, offset_y),
            textcoords="offset points",
            ha="center", va="bottom",
            color=theme_color, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=theme_color, alpha=1.0, lw=1),
            arrowprops=dict(arrowstyle="->", color=theme_color, lw=1)
        )

# --- X-axis Tick Label Coloring ---
plt.xticks(rotation=45, ha="right")
labels = ax.get_xticklabels()

for i, label in enumerate(labels):
    note_val = df.iloc[i]["note"]

    if pd.notna(note_val) and str(note_val).strip() != "":
        note_s = str(note_val).lower()

        if "(eew)" in note_s:
            tick_color = "green"
        elif "(pws)" in note_s:
            tick_color = "darkorange"
        else:
            tick_color = "red"

        label.set_fontweight("bold")
    else:
        tick_color = "black"
        label.set_fontweight("normal")

    label.set_color(tick_color)

# --- Final styling ---
ax.axhline(y=0, color="gray", linestyle="-", alpha=0.5)
ax.set_ylabel("Processing Time [seconds]", fontsize=12)
ax.set_xlabel("Report ID", fontsize=12)
ax.set_title(f"Alert Latency relative to Origin Time\n(Origin: {ref_time})", fontsize=14)
margin = max(5, y_max * 0.1)
if y_min == y_max:
    y_min -= 1
    y_max += 1
pad = max(5, (y_max - y_min) * 0.1)
ax.set_ylim(y_min - pad, y_max + pad)
ax.grid(axis="y", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig("outputs/06_EEW_PT_pfile.png", dpi=300)
print("EEW_processing_time Done")
