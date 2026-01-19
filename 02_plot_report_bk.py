#!/bin/python
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from obspy.geodetics import gps2dist_azimuth
import eewrep_function
import math
import re
import argparse

# === ERR event info ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot EEW report summary"
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
        raise FileNotFoundError("找不到對應的 XML 檔案")

    if eq_info:
        print(">> 成功讀取時間、地點、規模")
        report = eq_info["reportContent"]

        m = re.match(r"(\d{2})/(\d{2})-\d{2}:\d{2}(.*)發生規模([\d.]+)有感地震", report)
        if m:
            month, day, location, magnitude = m.groups()
            roc_year = int(year) - 1911
            lines = [
                f"{roc_year}年{int(month)}月{int(day)}日",
                f"{location}  規模{magnitude}地震"
            ]
        else:
            # 若格式不符合，直接放整行文字
            print("格式不符合，直接放整行文字")
            lines = [report]

ref_lat, ref_lon = eq_info["epicenterLat"], eq_info["epicenterLon"]
ref_mag, ref_dep = eq_info["magnitude"], eq_info["depth"]
ref_time = eq_info["ot"]

# === EER rep ===
INPUT_PATH = "./outputs/summary_20_192.txt"
df = pd.read_csv(INPUT_PATH, sep=r'\s+')
for col in ['Mag', 'Lat', 'Lon', 'Depth', 'Ma.']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 合併被切開的時間 (Date + Time)
# df['Report_time'] = df['Date'].str.replace('-', '') + ' ' + df['Time']
# df = df.drop(columns=['Date', 'Time'])
print(df)

df['Tdiff'] = pd.to_datetime(df['Report_time'], utc=True, errors='coerce') - ref_time
df['Tdiff_second'] = df['Tdiff'].dt.total_seconds()
df['H_error_km'] = df.apply(
    lambda row: eewrep_function.cal_horizontal_error(row['Lat'], row['Lon'], ref_lat, ref_lon)
    if pd.notna(row['Lat']) and pd.notna(row['Lon'])
    else float('nan'),
    axis=1
)

# === Plot ===
fig, axs = plt.subplots(2, 2, figsize=(14,10))
axs = axs.flatten()

# 1 Tdiff vs Mag
axs[0].plot(df['Tdiff_second'], df['Mag'], marker='o', linestyle='-', color='b')
axs[0].axhspan(ref_mag - 0.02, ref_mag + 0.02, color='orange', alpha=0.3, label='Target Zone')
axs[0].axhline(y = ref_mag, linestyle='--', color='gray')
axs[0].set_ylabel("Magnitude")
axs[0].set_title("Magnitude vs Processing Time")
axs[0].grid(True)

# 2 Tdiff vs Distance
dist_mask = df['Tdiff_second'].notna() & df['H_error_km'].notna()
if dist_mask.any():
    axs[1].plot(df.loc[dist_mask, 'Tdiff_second'], df.loc[dist_mask, 'H_error_km'],
               marker='o', linestyle='-', color='r')
    axs[1].axhspan(0, 0.3, color='orange', alpha=0.3, label='Target Zone')
    axs[1].axhline(y=0, linestyle='--', color='gray')
    axs[1].set_ylabel("Horizontal Error (km)")
    axs[1].set_title("Horizontal Error vs Processing Time")
    axs[1].grid(True)
    axs[1].invert_yaxis()
else:
    axs[1].text(0.5, 0.5, "No valid distance data", ha='center', va='center')
    axs[1].set_axis_off()

# 3 Tdiff vs Depth
axs[2].plot(df['Tdiff_second'], df['Depth'], marker='o', linestyle='-', color='g')
axs[2].axhspan(ref_dep - 1, ref_dep + 1, color='orange', alpha=0.3, label='Target Zone')
axs[2].axhline(y = ref_dep, linestyle='--', color='gray')
axs[2].set_ylabel("Depth (km)")
axs[2].set_title("Depth vs Processing Time")
axs[2].grid(True)
axs[2].invert_yaxis()

# 4 Tdiff vs Ma.
axs[3].plot(df['Tdiff_second'], df['Ma.'], marker='o', linestyle='-', color='m')
axs[3].set_ylabel("Number of Stations (Ma.)")
axs[3].set_title("Number of Stations vs Processing Time")
axs[3].grid(True)

# Xticks
for ax in axs:
    ax.set_xlabel("Processing Time(s)")
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))

fig.suptitle("01.21 Dapu Earthquake EEW report", fontsize=16)
plt.tight_layout()
plt.savefig("outputs/02_Report.png", dpi = 300)
print(">>> PNG saved.")
