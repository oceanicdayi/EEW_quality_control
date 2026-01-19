#!/bin/python
import argparse
import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
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
    dep = float(tmp[34:40])

    pfile_info = {}
    pfile_info["ori_time"] = dt
    pfile_info["mag"] = mag
    pfile_info["dep"] = dep
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
        description="Plot EEW report summary (Pfile input)"
    )
    parser.add_argument(
        "pfile",
        help="要讀取的 Pfile 檔名，例如 17010623.P20"
    )
    parser.add_argument(
        "--kind",
        choices=["f42", "f43", "gei", "all"],
        default="all",
        help="選擇分析類型：f42 / f43 / gei（預設 all）"
    )
    parser.add_argument(
        "--base-folder",
        default="./192",
        help="rep 檔案所在目錄（預設 ./192）"
    )
    parser.add_argument(
        "--xmin",
        type=float,
        default=None,
        help="x 軸最小值（秒）"
    )
    parser.add_argument(
        "--xmax",
        type=float,
        default=None,
        help="x 軸最大值（秒）"
    )
    parser.add_argument(
        "--xstep",
        type=float,
        default=2.0,
        help="x 軸刻度間隔（秒），預設 2"
    )
    args = parser.parse_args()

    pfile_info = unpackPfile(args.pfile)
    if not pfile_info:
        raise FileNotFoundError("找不到對應的 Pfile 檔案")

    ref_lat = None
    ref_lon = None
    ref_dep = None
    ref_mag = pfile_info["mag"]
    ref_dep = pfile_info["dep"]
    ref_time = pfile_info["ori_time"]

    print(">> 成功讀取時間、規模 (Pfile)")
    print(f"ref_mag: {ref_mag}")
    print(f"ref_dep: {ref_dep}")

# === EER rep ===
basefolder_name = os.path.basename(os.path.normpath(args.base_folder))
pfilename = os.path.splitext(os.path.basename(args.pfile))[0]
INPUT_PATH = f"./outputs/summary_{basefolder_name}_{pfilename}.txt"
df = pd.read_csv(INPUT_PATH, sep=r"\s+")
if args.kind != "all":
    df = df[df["Repfile"].astype(str).str.contains(f"_{args.kind}")].copy()
    if df.empty:
        raise ValueError(f"summary 檔內沒有 {args.kind} 類型資料")
for col in ["Mag", "Lat", "Lon", "Depth", "Ma.", ]:
    if col == "Report_time":
        df[col] = df["Date"].str.replace("-", "") + " " + df["Time"]
    else:
        df[col] = df[col].astype(float)

print(df)

# 合併被切開的時間 (Date + Time)
# df['Report_time'] = df['Date'].str.replace('-', '') + ' ' + df['Time']
# df = df.drop(columns=['Date', 'Time'])

df["Tdiff"] = pd.to_datetime(df["Report_time"]) - ref_time
df["Tdiff_second"] = df["Tdiff"].dt.total_seconds()

# If Pfile has no epicenter, fallback to max-magnitude location from summary
if ref_lat is None or ref_lon is None:
    if "Mag" in df.columns and "Lat" in df.columns and "Lon" in df.columns:
        idx = df["Mag"].idxmax()
        if pd.notna(idx):
            ref_lat = float(df.loc[idx, "Lat"]) if ref_lat is None else ref_lat
            ref_lon = float(df.loc[idx, "Lon"]) if ref_lon is None else ref_lon

if ref_lat is not None and ref_lon is not None:
    df["H_error_km"] = df.apply(
        lambda row: eewrep_function.cal_horizontal_error(
            row["Lat"], row["Lon"], ref_lat, ref_lon
        ),
        axis=1,
    )
else:
    df["H_error_km"] = np.nan

# === Plot ===
df["Repfile_short"] = df["Repfile"].astype(str).str.extract(r"_n(\d+)", expand=False).map(
    lambda v: f"n{v}" if pd.notna(v) else None
)
if df["Repfile_short"].isna().any():
    df["Repfile_short"] = df["Repfile"].astype(str)
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
axs = axs.flatten()

# 1 Tdiff vs Mag
axs[0].plot(df["Tdiff_second"], df["Mag"], marker="o", linestyle="-", color="b")
axs[0].axhspan(ref_mag - 0.02, ref_mag + 0.02, color="orange", alpha=0.3, label="Target Zone")
axs[0].axhline(y=ref_mag, linestyle="--", color="gray")
axs[0].set_ylabel("Magnitude")
axs[0].set_title("Magnitude vs Processing Time")
axs[0].grid(True)

# Annotate n1, n2, n3...
for _, row in df.iterrows():
    if pd.notna(row["Tdiff_second"]) and pd.notna(row["Mag"]):
        axs[0].annotate(
            row["Repfile_short"],
            (row["Tdiff_second"], row["Mag"]),
            textcoords="offset points",
            xytext=(0, 6),
            ha="center",
            fontsize=8,
            color="black",
        )

# 2 Tdiff vs Distance
if ref_lat is not None and ref_lon is not None:
    axs[1].plot(df["Tdiff_second"], df["H_error_km"], marker="o", linestyle="-", color="r")
    axs[1].axhspan(0, 0.3, color="orange", alpha=0.3, label="Target Zone")
    axs[1].axhline(y=0, linestyle="--", color="gray")
    axs[1].set_ylabel("Horizontal Error (km)")
    axs[1].set_title("Horizontal Error vs Processing Time")
    axs[1].grid(True)
    axs[1].invert_yaxis()
else:
    axs[1].text(0.5, 0.5, "No epicenter in Pfile", ha="center", va="center")
    axs[1].set_axis_off()

# 3 Tdiff vs Depth
axs[2].plot(df["Tdiff_second"], df["Depth"], marker="o", linestyle="-", color="g")
if ref_dep is not None:
    axs[2].axhspan(ref_dep - 1, ref_dep + 1, color="orange", alpha=0.3, label="Target Zone")
    axs[2].axhline(y=ref_dep, linestyle="--", color="gray")
axs[2].set_ylabel("Depth (km)")
axs[2].set_title("Depth vs Processing Time")
axs[2].grid(True)
axs[2].invert_yaxis()

# 4 Tdiff vs Ma.
axs[3].plot(df["Tdiff_second"], df["Ma."], marker="o", linestyle="-", color="m")
axs[3].set_ylabel("Number of Stations (Ma.)")
axs[3].set_title("Number of Stations vs Processing Time")
axs[3].grid(True)

# Xticks
for ax in axs:
    ax.set_xlabel("Processing Time(s)")
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%d"))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(args.xstep))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))

    if args.xmin is not None or args.xmax is not None:
        ax.set_xlim(left=args.xmin, right=args.xmax)


fig.suptitle("EEW report (Pfile)", fontsize=16)
plt.tight_layout()
plt.savefig("outputs/02_Report_pfile.png", dpi=300)
print(">>> PNG saved.")
