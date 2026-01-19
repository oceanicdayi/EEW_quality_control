import argparse
import pygmt
import pandas as pd
import numpy as np

# --- 1. 基本設定與參數 ---
parser = argparse.ArgumentParser(description="Plot TSMIP trigger map")
parser.add_argument("rep_path", help="rep 檔案路徑，例如 ./192/20250120161735_192_n10_f43.rep")
parser.add_argument("--epi-lon", type=float, required=True, help="震央經度")
parser.add_argument("--epi-lat", type=float, required=True, help="震央緯度")
args = parser.parse_args()

rep_path = args.rep_path
tsmip_path = "station.txt"
gmt_file = "city_2016.gmt"
epicenter_lon, epicenter_lat = args.epi_lon, args.epi_lat

# --- 2. 讀取資料 ---

# (A) 讀取所有 TSMIP 測站
# 格式：Station, Lon, Lat, Value
tsmip_all = pd.read_csv(tsmip_path, sep=r'\s+', header=None, names=['Station', 'Lon', 'Lat', 'Detph'])

# (B) 讀取 .rep 檔案 (實際使用的測站)
# 跳過標頭，抓取 Sta, Lat, Lon, PGA, PGV, PGD (對應索引 0, 4, 5, 6, 7, 8)
rep_used = pd.read_csv(
    rep_path, 
    sep=r'\s+', 
    skiprows=5, 
    header=None,
    usecols=[0, 4, 5, 6, 7, 8],
    names=['Station', 'Lat', 'Lon', 'PGA', 'PGV', 'PGD']
)

# --- 3. 計算最遠距離與繪圖範圍 ---
# 手動計算距離 (Haversine) 以確保準確性
def get_dist(lon, lat):
    return 6371 * 2 * np.arcsin(np.sqrt(
        np.sin(np.radians(lat - epicenter_lat)/2)**2 +
        np.cos(np.radians(epicenter_lat)) * np.cos(np.radians(lat)) * np.sin(np.radians(lon - epicenter_lon)/2)**2
    ))

rep_used['Dist'] = get_dist(rep_used['Lon'], rep_used['Lat'])
max_dist_km = rep_used['Dist'].max()

# --- 4. PyGMT 繪圖 ---
fig = pygmt.Figure()

# 設定範圍：涵蓋最遠測站
buffer = (max_dist_km / 111) + 0.3
region = [epicenter_lon - buffer, epicenter_lon + buffer, 
          epicenter_lat - buffer, epicenter_lat + buffer]

# 繪製綠地藍海底圖
fig.coast(region=region, projection="M15c", land="palegreen3", water="skyblue", 
          shorelines="0.8p,black", borders=["1/0.8p,black", "2/0.4p,gray30"], frame=True, resolution="h")
fig.plot(data=gmt_file, pen="0.5p,black")

# 圖層 1: 繪製所有 TSMIP 測站 (灰色三角形，置於底層)
fig.plot(
    x=tsmip_all['Lon'], 
    y=tsmip_all['Lat'], 
    style="t0.25c", 
    fill="gray80", 
    pen="0.1p,gray40"
)

# 圖層 2: 繪製資料內「有使用」的測站 (紅色三角形，置於頂層)
fig.plot(
    x=rep_used['Lon'], 
    y=rep_used['Lat'], 
    style="t0.35c", 
    fill="red", 
    pen="0.5p,black"
)

# 圖層 3: 繪製最遠距離範圍圓圈 (橘色虛線)
fig.plot(
    x=epicenter_lon, 
    y=epicenter_lat, 
    style=f"E-{max_dist_km * 2}k", 
    pen="1.2p,orange,dashed", 
    transparency=20
)

# 圖層 4: 繪製震央 (紅色星號)
fig.plot(x=epicenter_lon, y=epicenter_lat, style="a0.8c", fill="yellow", pen="1p,red")

# 圖層 5: 標註最遠測站資訊
farthest_sta = rep_used.loc[rep_used['Dist'].idxmax(), 'Station']
fig.text(
    x=epicenter_lon, 
    y=epicenter_lat + (max_dist_km/111) + 0.05, 
    text=f"Trigger Limit: {max_dist_km:.1f} km ({farthest_sta})",
    font="11p,Helvetica-Bold,orange", 
    justify="BC", 
    fill="white@20"
)

# --- 6. 計算觸發率 (Trigger Ratio) ---

# 計算所有 TSMIP 測站到震央的距離
tsmip_all['Dist'] = get_dist(tsmip_all['Lon'], tsmip_all['Lat'])

# 找出在 max_dist_km 範圍內的所有測站 (分母)
stations_within_range = tsmip_all[tsmip_all['Dist'] <= max_dist_km]
print(stations_within_range,'\n')
total_in_range = len(stations_within_range)

# 找出在 max_dist_km 範圍內且有被使用的測站 (分子)
# (通常 .rep 裡的站都在範圍內，但為了保險我們再過濾一次)
triggered_in_range = len(rep_used[rep_used['Dist'] <= max_dist_km])
print(rep_used)

# 計算比率
if total_in_range > 0:
    trigger_ratio = (triggered_in_range / total_in_range) * 100
else:
    trigger_ratio = 0

print(f"半徑 {max_dist_km:.2f}km 內總站數: {total_in_range}")
print(f"半徑內觸發站數: {triggered_in_range}")
print(f"觸發比率: {trigger_ratio:.2f}%")

# --- 7. 在地圖上新增文字描述 ---

# 我們將文字放在地圖的左上角 (TL) 或下方
fig.text(
    position="TL",               # Top-Left 對齊
    text=f"Trigger Ratio within Range: {trigger_ratio:.1f}% ({triggered_in_range}/{total_in_range})",
    font="14p,Helvetica-Bold,black",
    fill="white@20",             # 半透明白色底塊讓文字清晰
    offset="0.5c/-0.5c",         # 從左上角往內偏移
    justify="TL"
)

fig.savefig("outputs/04_Trigger_map.png")
